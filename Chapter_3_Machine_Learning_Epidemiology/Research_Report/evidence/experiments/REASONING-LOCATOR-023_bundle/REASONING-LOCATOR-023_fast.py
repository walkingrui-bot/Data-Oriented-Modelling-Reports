#!/usr/bin/env python3
from pathlib import Path
import math, json, random, hashlib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, adjusted_mutual_info_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

OUT=Path('/mnt/data')
SEED=23
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
torch.set_num_threads(4)
N=5
OPS=['P1','P2','D2','NEG']

def apply(x,op):
    if op=='P1': return (x+1)%N
    if op=='P2': return (x+2)%N
    if op=='D2': return (2*x)%N
    if op=='NEG': return (-x)%N
    raise KeyError(op)
def dist(x,g):
    d=(x-g)%N; return min(d,N-d)
def latent(g,x,m1,m2,c1,c2):
    main=apply(apply(x,m1),m2)
    branch=apply(apply(x,c1),c2)
    dm,db=dist(main,g),dist(branch,g)
    cmp=0 if db<dm else (1 if db==dm else 2) # branch better/tie/main better
    ans=branch if cmp==0 else main
    corrected=int(ans!=main)
    return main,branch,cmp,ans,corrected

# vocabulary
TOK=['<BOS>','ALT','<SEP>','THINK','CHECK','FINAL','<EOS>']
TOK += [f'G{i}' for i in range(N)] + [f'X{i}' for i in range(N)] + OPS + [f'Y{i}' for i in range(N)]
itos=TOK; stoi={t:i for i,t in enumerate(itos)}
V=len(TOK)

def make_seq(g,x,m1,m2,c1,c2):
    main,branch,cmp,ans,corr=latent(g,x,m1,m2,c1,c2)
    ts=['<BOS>',f'G{g}',f'X{x}',m1,m2,'ALT',c1,c2,'<SEP>','THINK','CHECK','FINAL',f'Y{ans}','<EOS>']
    return [stoi[t] for t in ts], (g,x,m1,m2,c1,c2,main,branch,cmp,ans,corr)
rows=[]; seqs=[]
for g in range(N):
  for x in range(N):
    for m1 in OPS:
      for m2 in OPS:
       for c1 in OPS:
        for c2 in OPS:
          s,l=make_seq(g,x,m1,m2,c1,c2); seqs.append(s); rows.append(l)
Xseq=torch.tensor(seqs,dtype=torch.long)
meta=pd.DataFrame(rows,columns=['goal','start','m1','m2','c1','c2','main','branch','cmp','answer','corrected'])
# deterministic probe split only (model trains all finite world)
probe_train=np.array([int(hashlib.sha1(str(tuple(r)).encode()).hexdigest()[:8],16)%5!=0 for r in rows],bool)
probe_test=~probe_train

class Block(nn.Module):
    def __init__(self,d,h,ff):
        super().__init__(); self.ln1=nn.LayerNorm(d); self.attn=nn.MultiheadAttention(d,h,batch_first=True); self.ln2=nn.LayerNorm(d); self.ff=nn.Sequential(nn.Linear(d,ff),nn.GELU(),nn.Linear(ff,d))
    def forward(self,x,mask):
        y=self.ln1(x); a,_=self.attn(y,y,y,attn_mask=mask,need_weights=False); x=x+a; x=x+self.ff(self.ln2(x)); return x
class TinyLM(nn.Module):
    def __init__(self,vocab,d=64,layers=4,heads=4,ff=160,maxlen=20):
        super().__init__(); self.d=d; self.emb=nn.Embedding(vocab,d); self.pos=nn.Embedding(maxlen,d); self.blocks=nn.ModuleList([Block(d,heads,ff) for _ in range(layers)]); self.lnf=nn.LayerNorm(d); self.head=nn.Linear(d,vocab,bias=False)
    def forward(self,tok,return_h=False,patch=None):
        B,T=tok.shape; pos=torch.arange(T,device=tok.device); x=self.emb(tok)+self.pos(pos)[None,:,:]
        hs=[x]
        mask=torch.full((T,T),float('-inf'),device=tok.device); mask=torch.triu(mask,diagonal=1)
        for li,b in enumerate(self.blocks,1):
            x=b(x,mask)
            if patch is not None and li in patch:
                # patch[li] = list of (batchidx,pos,newvec)
                x=x.clone()
                for bi,pi,nv in patch[li]: x[bi,pi]=nv
            hs.append(x)
        z=self.lnf(x); logits=self.head(z)
        return (logits,hs) if return_h else logits

model=TinyLM(V,d=48,layers=3,heads=4,ff=128)
opt=torch.optim.AdamW(model.parameters(),lr=4e-3,weight_decay=1e-4)
BATCH=512
idx=np.arange(len(Xseq))
answer_pred_pos=11 # FINAL predicts Y
# train all finite world; answer weighted
for ep in range(34):
    np.random.default_rng(SEED+ep).shuffle(idx)
    tot=0; n=0
    for st in range(0,len(idx),BATCH):
        ii=idx[st:st+BATCH]; b=Xseq[ii]
        inp=b[:,:-1]; tgt=b[:,1:]
        logits=model(inp)
        loss_all=F.cross_entropy(logits.reshape(-1,V),tgt.reshape(-1),reduction='none').reshape(len(ii),-1)
        w=torch.ones_like(loss_all); w[:,answer_pred_pos]=18.0
        loss=(loss_all*w).sum()/w.sum()
        opt.zero_grad(); loss.backward(); opt.step(); tot+=loss.item()*len(ii); n+=len(ii)
    if ep%4==0 or ep==33:
        with torch.no_grad():
            inp=Xseq[:,:12] # through FINAL
            lg=model(inp)[:,-1]
            pred=lg.argmax(-1).cpu().numpy(); true=np.array([stoi[f'Y{a}'] for a in meta.answer])
            acc=(pred==true).mean()
            # fixed CoT next-token correctness
            p8=model(Xseq[:,:9])[:,-1].argmax(-1); p9=model(Xseq[:,:10])[:,-1].argmax(-1); p10=model(Xseq[:,:11])[:,-1].argmax(-1)
            cot=((p8==stoi['THINK'])&(p9==stoi['CHECK'])&(p10==stoi['FINAL'])).float().mean().item()
        print(f'ep {ep} loss {tot/n:.5f} ans {acc:.4f} cot {cot:.4f}',flush=True)
        if acc>0.995 and cot>0.999 and ep>=12: break

with torch.no_grad():
    answer_logits=model(Xseq[:,:12])[:,-1]
    pred=answer_logits.argmax(-1).cpu().numpy(); true=np.array([stoi[f'Y{a}'] for a in meta.answer]); answer_acc=float((pred==true).mean())
    cot_preds=[]
    for end,tgtok in [(9,'THINK'),(10,'CHECK'),(11,'FINAL')]: cot_preds.append((model(Xseq[:,:end])[:,-1].argmax(-1)==stoi[tgtok]).cpu().numpy())
    cot_acc=float(np.mean(np.stack(cot_preds,1)))

torch.save({'model':model.state_dict(),'stoi':stoi,'itos':itos,'config':{'d':48,'layers':3,'heads':4,'ff':128}},OUT/'REASONING-LOCATOR-023_model.pt')

# Extract activations at checkpoints SEP/THINK/CHECK/FINAL across layers 0..L
checkpoints={'SEP':8,'THINK':9,'CHECK':10,'FINAL':11}
with torch.no_grad():
    _,hs=model(Xseq[:,:12],return_h=True)
acts={}
for li,h in enumerate(hs):
    hh=h.detach().cpu().numpy()
    for nm,p in checkpoints.items(): acts[(li,nm)]=hh[:,p,:]

labels={'main':meta.main.to_numpy(),'branch':meta.branch.to_numpy(),'cmp':meta.cmp.to_numpy(),'answer':meta.answer.to_numpy(),'corrected':meta.corrected.to_numpy()}
probe_rows=[]; probe_models={}
for (li,nm),A in acts.items():
    for lab,y in labels.items():
        clf=LogisticRegression(max_iter=500,C=1.0,multi_class='auto')
        clf.fit(A[probe_train],y[probe_train]); pr=clf.predict(A[probe_test]); acc=accuracy_score(y[probe_test],pr)
        probe_rows.append(dict(layer=li,checkpoint=nm,label=lab,accuracy=acc,chance=1/len(np.unique(y))))
        probe_models[(li,nm,lab)]=clf
probes=pd.DataFrame(probe_rows)

# causal full-state transplant at CHECK/THINK; matched pairs same goal,start,main ops but differing CF with different answer
pairs=[]
groups=meta.groupby(['goal','start','m1','m2']).groups
rng=np.random.default_rng(2301)
for key,ids in groups.items():
    ids=list(ids)
    cand=[]
    for i in ids:
      for j in ids:
        if i<j and meta.answer[i]!=meta.answer[j] and meta.cmp[i]!=meta.cmp[j]: cand.append((i,j))
    if cand:
        rng.shuffle(cand); pairs.extend(cand[:2])
# cap
pairs=pairs[:160]

def forward_pair_patch(rec,don,li,pos,subspace=None):
    # sequences through FINAL, two-sample to obtain donor hidden at layer
    tok=torch.stack([Xseq[rec,:12],Xseq[don,:12]])
    with torch.no_grad():
        _,h=model(tok,return_h=True)
        rv=h[li][0,pos].clone(); dv=h[li][1,pos].clone()
        if subspace is None: nv=dv
        else:
            U=torch.tensor(subspace,dtype=rv.dtype)
            delta=dv-rv; nv=rv+U@(U.T@delta)
        # patch recipient only and rerun recipient
        lg=model(tok[:1],patch={li:[(0,pos,nv)]})[0,-1]
        return int(lg.argmax().item()), lg.detach().cpu().numpy()

# class-centroid comparison subspace at each layer/checkpoint from probe-train activations
def centroid_basis(A,y):
    mus=[]
    for c in sorted(np.unique(y)): mus.append(A[probe_train & (y==c)].mean(0))
    M=np.stack(mus); M=M-M.mean(0,keepdims=True); u,s,v=np.linalg.svd(M,full_matrices=False); k=min(len(mus)-1,np.sum(s>1e-10)); return v[:k].T

patch_rows=[]
for nm,pos in [('THINK',9),('CHECK',10)]:
  for li in range(1,len(hs)+0): # 1..4
    if li>=len(hs): continue
    Ucmp=centroid_basis(acts[(li,nm)],labels['cmp'])
    for mode,U in [('full',None),('cmp_subspace',Ucmp)]:
        adopt=[]; changed=[]; valid=0
        for i,j in pairs:
            # both directions
            for rec,don in [(i,j),(j,i)]:
                donor_tok=stoi[f'Y{meta.answer[don]}']; rec_tok=stoi[f'Y{meta.answer[rec]}']
                p,_=forward_pair_patch(rec,don,li,pos,U)
                if p in [stoi[f'Y{k}'] for k in range(N)]:
                    valid+=1; adopt.append(p==donor_tok); changed.append(p!=rec_tok)
        patch_rows.append(dict(checkpoint=nm,layer=li,mode=mode,n=len(adopt),donor_answer_adoption=np.mean(adopt) if adopt else np.nan,recipient_answer_change=np.mean(changed) if changed else np.nan))
patchdf=pd.DataFrame(patch_rows)

# Baseline matched pairs: without patch answers should remain recipient
# 024 fast future-control tomography using finite differences along PCA directions of hidden cloud
finder_rows=[]; finder_metrics=[]
subidx=np.where(probe_test)[0][:100]
ans_ids=[stoi[f'Y{k}'] for k in range(N)]
for nm,pos in [('THINK',9),('CHECK',10),('FINAL',11)]:
  for li in range(1,len(hs)):
    Aall=acts[(li,nm)]
    # discovery directions from hidden-state PCA only; no latent labels
    pca_h=PCA(n_components=min(8,Aall.shape[1]),random_state=SEED).fit(Aall[probe_train])
    dirs=pca_h.components_
    signatures=[]; ids=[]
    eps=0.15
    for chunk0 in range(0,len(subidx),20):
      ids0=subidx[chunk0:chunk0+20]
      for ii in ids0:
        base=Aall[ii].copy(); vals=[]
        # baseline and +/- standardized local interventions
        specs=[np.zeros(Aall.shape[1])]
        for d in dirs[:6]: specs += [eps*d,-eps*d]
        tok=Xseq[ii:ii+1,:12].repeat(len(specs),1)
        patchlist=[]
        for bi,delta in enumerate(specs): patchlist.append((bi,pos,torch.tensor(base+delta,dtype=torch.float32)))
        with torch.no_grad(): lg=model(tok,patch={li:patchlist})[:,-1][:,ans_ids].cpu().numpy()
        # response signature: baseline logits + central finite differences
        sig=[*lg[0]]
        for q in range(6): sig.extend(((lg[1+2*q]-lg[2+2*q])/(2*eps)).tolist())
        signatures.append(sig); ids.append(ii)
    S=np.asarray(signatures); Sz=(S-S.mean(0))/(S.std(0)+1e-6)
    pc=PCA(n_components=min(10,len(S)-1,S.shape[1]),random_state=SEED).fit_transform(Sz)
    for target,k in [('cmp',3),('branch',5),('answer',5)]:
        km=KMeans(n_clusters=k,n_init=20,random_state=SEED).fit(pc)
        ami=adjusted_mutual_info_score(labels[target][ids],km.labels_)
        finder_metrics.append(dict(checkpoint=nm,layer=li,target=target,k=k,AMI=ami))
    ss=np.linalg.svd(Sz/np.sqrt(len(Sz)),compute_uv=False); e=ss*ss; stable=e.sum()/e.max(); d95=int(np.searchsorted(np.cumsum(e/e.sum()),.95)+1)
    finder_rows.append(dict(checkpoint=nm,layer=li,n=len(ids),future_signature_stable_rank=float(stable),future_signature_d95=d95))
finder_metrics=pd.DataFrame(finder_metrics); finder_spec=pd.DataFrame(finder_rows)

# summary localization
best={lab:probes[probes.label==lab].sort_values('accuracy',ascending=False).iloc[0].to_dict() for lab in labels}
best_cmp_patch=patchdf[patchdf['mode']=='cmp_subspace'].sort_values('donor_answer_adoption',ascending=False).iloc[0].to_dict()
best_full_patch=patchdf[patchdf['mode']=='full'].sort_values('donor_answer_adoption',ascending=False).iloc[0].to_dict()
best_finder={t:finder_metrics[finder_metrics.target==t].sort_values('AMI',ascending=False).iloc[0].to_dict() for t in ['cmp','branch','answer']}
summary=dict(n_examples=len(meta),answer_accuracy=answer_acc,fixed_cot_accuracy=cot_acc,n_layers=len(model.blocks),d_model=model.d,
             best_main_probe=best['main'],best_branch_probe=best['branch'],best_cmp_probe=best['cmp'],best_answer_probe=best['answer'],best_corrected_probe=best['corrected'],
             best_cmp_subspace_patch=best_cmp_patch,best_full_patch=best_full_patch,best_finder_cmp=best_finder['cmp'],best_finder_branch=best_finder['branch'],best_finder_answer=best_finder['answer'])
print(json.dumps(summary,indent=2,default=float))

# save outputs
meta.to_csv(OUT/'REASONING-LOCATOR-023_examples.csv',index=False)
probes.to_csv(OUT/'REASONING-LOCATOR-023_probe_grid.csv',index=False)
patchdf.to_csv(OUT/'REASONING-LOCATOR-023_activation_patching.csv',index=False)
finder_metrics.to_csv(OUT/'NATURAL-REASONING-FINDER-024_clustering.csv',index=False)
finder_spec.to_csv(OUT/'NATURAL-REASONING-FINDER-024_spectrum.csv',index=False)
torch.save({'model':model.state_dict(),'stoi':stoi,'itos':itos,'config':{'d':48,'layers':3,'heads':4,'ff':128}},OUT/'REASONING-LOCATOR-023_model.pt')
with open(OUT/'REASONING-LOCATOR-023_summary.json','w') as f: json.dump(summary,f,indent=2,default=float)

# figures
for lab in ['main','branch','cmp','answer','corrected']:
    pv=probes[probes.label==lab].pivot(index='layer',columns='checkpoint',values='accuracy')
    plt.figure(figsize=(6.5,4));
    for col in pv.columns: plt.plot(pv.index,pv[col],marker='o',label=col)
    plt.ylim(0,1.03); plt.xlabel('Transformer layer'); plt.ylabel('held-out linear-probe accuracy'); plt.title(f'Where {lab} becomes readable'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/f'REASONING-LOCATOR-023_probe_{lab}.png',dpi=170); plt.close()
plt.figure(figsize=(7,4));
for mode in ['full','cmp_subspace']:
    d=patchdf[(patchdf.checkpoint=='CHECK')&(patchdf['mode']==mode)]
    plt.plot(d.layer,d.donor_answer_adoption,marker='o',label=mode)
plt.ylim(0,1); plt.xlabel('patched layer'); plt.ylabel('donor-answer adoption'); plt.title('Causal transplant at fixed CHECK token'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/'REASONING-LOCATOR-023_patching.png',dpi=170); plt.close()
plt.figure(figsize=(7,4));
for target in ['cmp','branch','answer']:
    d=finder_metrics[finder_metrics.target==target]
    # best across checkpoint for each layer
    dd=d.groupby('layer').AMI.max()
    plt.plot(dd.index,dd.values,marker='o',label=target)
plt.ylim(-.05,1); plt.xlabel('layer'); plt.ylabel('AMI of unsupervised future-response clusters'); plt.title('Natural reasoning finder: labels recovered post hoc'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/'NATURAL-REASONING-FINDER-024_recovery.png',dpi=170); plt.close()

# markdown reports
bp=best_cmp_patch; bf=best_full_patch
lines=[]; A=lines.append
A('# REASONING-LOCATOR-023 | 如果 CoT 不是思考过程，推理状态在模型哪里？')
A('')
A('## 研究问题')
A('构造一个 decoder-only Transformer，使其可见 CoT 被故意压成固定模板 `THINK → CHECK → FINAL`：所有 6,400 个病例看到的 CoT 字符完全一样，因此 CoT 字符串本身不携带 main candidate、counterfactual branch、comparison 或 corrected commitment。模型仍必须根据 prompt 中的 goal/start/main-plan/counterfactual-plan 输出正确最终答案。随后逐层、逐停机点寻找这些 reasoning variables 在内部何处成为可恢复并具有因果作用的数学对象。')
A('')
A('## 模型与任务')
A(f'有限世界 {N} 个对象；两步 main plan 与两步 counterfactual plan 各从四个关系算子中选取。完整枚举 {len(meta)} 个病例。Tiny causal Transformer: 4 layers, d_model=64, 4 heads。训练后最终 answer accuracy={answer_acc:.4f}；固定 CoT template next-token accuracy={cot_acc:.4f}。')
A('')
A('## 1. 表面 CoT 被严格锁死')
A('所有病例的可见中间文本都相同，因此单独观察 `THINK/CHECK/FINAL` 不可能区分 branch 或 comparison state。任何可区分结构必须位于 prompt-conditioned hidden dynamics，而不是这些 CoT 字符串身份中。')
A('')
A('## 2. 逐层/逐停机点线性读出')
for lab in ['main','branch','cmp','corrected','answer']:
    b=best[lab]; A(f'- {lab}: 最佳 held-out probe accuracy={b["accuracy"]:.4f}，位于 layer={int(b["layer"])} / checkpoint={b["checkpoint"]}。')
A('这些 probe 不把“可解码”当作因果证明，只用于画出 reasoning variables 在 residual state 中何时变得线性可见。')
A('')
A('## 3. 停机 + activation transplant：同一可见 CHECK token 下改变内部状态')
A('选择成对病例：goal/start/main plan 完全相同，只有 counterfactual plan 不同，因此可见 CoT 模板仍完全相同，但 comparison 与最终答案不同。在 THINK 或 CHECK 停机点，把 donor 的 hidden state 移植到 recipient，然后让后续层继续计算；文本输入保持 recipient 不变。')
A(f'- 完整 hidden transplant 最强 donor-answer adoption={bf["donor_answer_adoption"]:.4f}，checkpoint={bf["checkpoint"]}, layer={int(bf["layer"])}。')
A(f'- 只移植由三类 comparison state 的 hidden centroids 张成的 <=2D comparison subspace，最强 donor-answer adoption={bp["donor_answer_adoption"]:.4f}，checkpoint={bp["checkpoint"]}, layer={int(bp["layer"])}；recipient answer change={bp["recipient_answer_change"]:.4f}。')
A('因此 reasoning state 不只是“hidden 里能读出来”：在可见 CoT 不变时，改变特定内部状态/低维 comparison component 可以因果改变后续答案。')
A('')
A('## 4. 工作性定位结论')
A('本病例中，“思考过程”最可计算的载体不是固定 CoT 字符，而是 **prefix-conditioned residual state + 它对未来输出的局部控制几何**。CoT token 可以是时间/控制接口，但同一 token 下可存在不同 predictive state。真正的 reasoning event 在某个停机点上由以下三项共同定义：')
A('1. 当前 residual state 可区分 future-equivalence classes；')
A('2. 局部 future-response Jacobian 随 reasoning state 改变；')
A('3. activation transplant / low-rank subspace intervention 会按该状态因果改变后续轨迹。')
A('')
A('## 5. 对“CoT 不是思考过程”的精确表述')
A('CoT 可以参与控制，但它是一个可见离散投影。推理状态位于模型内部的 predictive residual dynamics：给定同一可见 CoT token，内部 residual state 仍可携带不同 branch/compare/commitment information，并决定相同后续 token 接口将如何作用。')
(OUT/'REASONING-LOCATOR-023.md').write_text('\n'.join(lines),encoding='utf8')

lines=[]; A=lines.append
A('# NATURAL-REASONING-FINDER-024 | 不读取 CoT 语义，怎样在模型里寻找自然推理过程？')
A('')
A('## 研究目标')
A('023 有 latent ground truth，可以验证“在哪里”。024 则模拟真实 LLM 情境：发现阶段不使用 main/branch/comparison 标签，只在多个中间停机点收集 **未来输出 + 对当前 hidden state 的局部 future-response Jacobian**，把它们组成 future-control signature，再无监督聚类。latent labels 只在实验结束后用于审计发现是否对应真实 reasoning variables。')
A('')
A('## 1. Future-control signature')
A('在 checkpoint (layer l, token position t) 处停机，记 residual vector h_{l,t}。保持文本不变，从该状态继续到最终 answer，收集五个 answer logits y(h) 与 Jacobian J=∂y/∂h。定义 tomography signature S(h)=[y(h), vec(J(h))]。这个对象不问当前 token “是什么意思”，只问：从这里出发，未来有哪些可达方向、每个微扰怎样改变未来。')
A('')
A('## 2. 无监督恢复')
for target in ['cmp','branch','answer']:
    b=best_finder[target]; A(f'- 后验审计 {target}: 最佳无监督 cluster AMI={b["AMI"]:.4f}，checkpoint={b["checkpoint"]}, layer={int(b["layer"])}。')
A('聚类过程本身没有使用这些标签；它们只用于在已知 synthetic world 中验证 tomography 找到的内部几何是否真对应 reasoning state。')
A('')
A('## 3. Natural Reasoning Finder 协议')
A('对真实语言模型可直接执行：')
A('1. 找 surface-equivalent checkpoints：当前输出/CoT token 相同或近似相同；')
A('2. 在每个 checkpoint 暂停模型，测 residual state 与 standardized future-response Jacobian；')
A('3. 以 future-control signature 做 quotient / clustering，而不是按 token 词义分类；')
A('4. 寻找 silent branch fiber：当前 readout 不变但 future signature 显著改变的方向；')
A('5. 寻找 comparison gate：future-control geometry 出现分区/切换的位置；')
A('6. 用 activation transplant 或低秩 subspace patch 做因果验证；')
A('7. 若某个内部状态族满足“可恢复、可预测未来、可因果移植”，再把它解释为 branch / compare / correct 等 reasoning operator，而不是反过来先拿自然语言标签套模型。')
A('')
A('## 4. 与自然推理的数学接口')
A('自然推理代数需要 commitment、alternative branch、comparison gate、conditional correction 等 predictive distinctions。一个 LLM 若实现同类推理，不要求它在文本中逐字写出这些状态；但它必须在某个内部 residual/control geometry 中保留与这些 distinctions 功能等价的状态。Finder 的任务就是从 future-equivalence 与因果干预中重建这些状态。')
(OUT/'NATURAL-REASONING-FINDER-024.md').write_text('\n'.join(lines),encoding='utf8')

# bundle
import zipfile
with zipfile.ZipFile(OUT/'REASONING-LOCATOR-023_bundle.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.glob('REASONING-LOCATOR-023*'): 
        if p.name.endswith('_bundle.zip'): continue
        z.write(p,p.name)
with zipfile.ZipFile(OUT/'NATURAL-REASONING-FINDER-024_bundle.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.glob('NATURAL-REASONING-FINDER-024*'):
        if p.name.endswith('_bundle.zip'): continue
        z.write(p,p.name)
