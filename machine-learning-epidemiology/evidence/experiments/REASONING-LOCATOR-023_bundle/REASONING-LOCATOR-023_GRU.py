#!/usr/bin/env python3
from pathlib import Path
import math, json, random, hashlib, zipfile
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

OUT=Path('/mnt/data'); SEED=2303
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.set_num_threads(6)
N=5; OPS=['P1','P2','D2','NEG']
def apply(x,o):
    return {'P1':(x+1)%N,'P2':(x+2)%N,'D2':(2*x)%N,'NEG':(-x)%N}[o]
def dist(x,g):
    d=(x-g)%N; return min(d,N-d)
def latent(g,x,m1,m2,c1,c2):
    main=apply(apply(x,m1),m2); branch=apply(apply(x,c1),c2)
    dm,db=dist(main,g),dist(branch,g)
    cmp=0 if db<dm else (1 if db==dm else 2)
    ans=branch if cmp==0 else main
    return main,branch,cmp,ans,int(ans!=main)
TOK=['<BOS>','ALT','<SEP>','THINK','CHECK','FINAL','<EOS>']+[f'G{i}' for i in range(N)]+[f'X{i}' for i in range(N)]+OPS+[f'Y{i}' for i in range(N)]
stoi={t:i for i,t in enumerate(TOK)}; V=len(TOK)
seqs=[]; rows=[]
for g in range(N):
 for x in range(N):
  for m1 in OPS:
   for m2 in OPS:
    for c1 in OPS:
     for c2 in OPS:
      main,branch,cmp,ans,corr=latent(g,x,m1,m2,c1,c2)
      ts=['<BOS>',f'G{g}',f'X{x}',m1,m2,'ALT',c1,c2,'<SEP>','THINK','CHECK','FINAL',f'Y{ans}','<EOS>']
      seqs.append([stoi[t] for t in ts]); rows.append((g,x,m1,m2,c1,c2,main,branch,cmp,ans,corr))
seq=torch.tensor(seqs,dtype=torch.long)
meta=pd.DataFrame(rows,columns=['goal','start','m1','m2','c1','c2','main','branch','cmp','answer','corrected'])
# probe split
probe_train=np.array([int(hashlib.sha1(str(r).encode()).hexdigest()[:8],16)%5!=0 for r in rows]); probe_test=~probe_train

class StackedGRULM(nn.Module):
    def __init__(self,vocab,emb=32,hid=64,layers=3):
        super().__init__(); self.hid=hid; self.layers=layers; self.emb=nn.Embedding(vocab,emb)
        self.cells=nn.ModuleList([nn.GRUCell(emb if i==0 else hid,hid) for i in range(layers)])
        self.head=nn.Linear(hid,vocab)
    def zero(self,B,device=None): return [torch.zeros(B,self.hid,device=device) for _ in range(self.layers)]
    def step(self,tok,hs):
        x=self.emb(tok)
        nh=[]
        for i,c in enumerate(self.cells):
            h=c(x,hs[i]); nh.append(h); x=h
        return self.head(nh[-1]),nh
    def forward(self,toks,return_states=False):
        B,T=toks.shape; hs=self.zero(B,toks.device); logits=[]; states=[[ ] for _ in range(self.layers)]
        for t in range(T):
            lg,hs=self.step(toks[:,t],hs); logits.append(lg)
            if return_states:
                for l in range(self.layers): states[l].append(hs[l])
        L=torch.stack(logits,1)
        if return_states:
            S=[torch.stack(s,1) for s in states]
            return L,S,hs
        return L
    def state_after(self,toks):
        B,T=toks.shape; hs=self.zero(B,toks.device)
        for t in range(T): _,hs=self.step(toks[:,t],hs)
        return [h.clone() for h in hs]
    def continue_from(self,hs,suffix):
        # suffix BxT, returns logits after each suffix token
        out=[]
        for t in range(suffix.shape[1]):
            lg,hs=self.step(suffix[:,t],hs); out.append(lg)
        return torch.stack(out,1) if out else None,hs

model=StackedGRULM(V)
opt=torch.optim.AdamW(model.parameters(),lr=5e-3,weight_decay=1e-5)
idx=np.arange(len(seq)); BATCH=1024
# next token positions we supervise: input pos8->THINK,9->CHECK,10->FINAL,11->answer,12->EOS
mask_positions=[8,9,10,11,12]
for ep in range(80):
    np.random.default_rng(SEED+ep).shuffle(idx)
    for st in range(0,len(idx),BATCH):
        ii=idx[st:st+BATCH]; b=seq[ii]; inp=b[:,:-1]; tgt=b[:,1:]
        lg=model(inp)
        loss_mat=F.cross_entropy(lg.reshape(-1,V),tgt.reshape(-1),reduction='none').reshape(len(ii),-1)
        w=torch.zeros_like(loss_mat); w[:,8:11]=1.; w[:,11]=10.; w[:,12]=1.
        loss=(loss_mat*w).sum()/w.sum()
        opt.zero_grad(); loss.backward(); opt.step()
    if ep%5==0 or ep==79:
        with torch.no_grad():
            lg=model(seq[:,:12]); ans_pred=lg[:,11].argmax(-1).numpy(); ans_true=np.array([stoi[f'Y{a}'] for a in meta.answer]); acc=(ans_pred==ans_true).mean()
            cot=((lg[:,8].argmax(-1)==stoi['THINK'])&(lg[:,9].argmax(-1)==stoi['CHECK'])&(lg[:,10].argmax(-1)==stoi['FINAL'])).float().mean().item()
        print(f'ep {ep} ans={acc:.4f} cot={cot:.4f}',flush=True)
        if acc>0.9995 and cot>0.9995 and ep>=15: break
with torch.no_grad():
    lg,states,_=model(seq[:,:12],return_states=True)
    ans_pred=lg[:,11].argmax(-1).numpy(); ans_true=np.array([stoi[f'Y{a}'] for a in meta.answer]); answer_acc=float((ans_pred==ans_true).mean())
    cot_acc=float(((lg[:,8].argmax(-1)==stoi['THINK'])&(lg[:,9].argmax(-1)==stoi['CHECK'])&(lg[:,10].argmax(-1)==stoi['FINAL'])).float().mean())
print('final',answer_acc,cot_acc,flush=True)
torch.save({'state_dict':model.state_dict(),'vocab':TOK,'config':{'emb':32,'hid':64,'layers':3}},OUT/'REASONING-LOCATOR-023_model.pt')

# Probe grid: layer x checkpoint
checkpoints={'SEP':8,'THINK':9,'CHECK':10,'FINAL':11}
acts={(l+1,nm):states[l][:,p,:].detach().numpy() for l in range(model.layers) for nm,p in checkpoints.items()}
labels={'main':meta.main.to_numpy(),'branch':meta.branch.to_numpy(),'cmp':meta.cmp.to_numpy(),'answer':meta.answer.to_numpy(),'corrected':meta.corrected.to_numpy()}
probe_rows=[]; probe_clf={}
for key,A in acts.items():
    li,nm=key
    for lab,y in labels.items():
        clf=LogisticRegression(max_iter=800,C=1.0)
        clf.fit(A[probe_train],y[probe_train]); pr=clf.predict(A[probe_test]); ac=accuracy_score(y[probe_test],pr)
        probe_rows.append(dict(layer=li,checkpoint=nm,label=lab,accuracy=ac,chance=1/len(np.unique(y))))
        probe_clf[(li,nm,lab)]=clf
probes=pd.DataFrame(probe_rows)

# matched donor-recipient pairs: same goal/start/main plan, different counterfactual, cmp and answer differ
pairs=[]; rng=np.random.default_rng(SEED)
for _,ids in meta.groupby(['goal','start','m1','m2']).groups.items():
    ids=list(ids); c=[]
    for ai in range(len(ids)):
      for bj in range(ai+1,len(ids)):
        i,j=ids[ai],ids[bj]
        if meta.answer[i]!=meta.answer[j] and meta.cmp[i]!=meta.cmp[j]: c.append((i,j))
    rng.shuffle(c); pairs.extend(c[:2])
pairs=pairs[:180]
ans_ids=[stoi[f'Y{k}'] for k in range(N)]

def centroid_basis(A,y):
    M=np.stack([A[probe_train & (y==c)].mean(0) for c in sorted(np.unique(y))]); M-=M.mean(0); u,s,v=np.linalg.svd(M,full_matrices=False); return v[:max(1,min(len(np.unique(y))-1,np.sum(s>1e-10)))].T

def predict_after_patch(rec,don,layer,pos,basis=None):
    # halt immediately after processing token at pos
    with torch.no_grad():
        hr=model.state_after(seq[rec:rec+1,:pos+1]); hd=model.state_after(seq[don:don+1,:pos+1])
        r=hr[layer-1][0]; d=hd[layer-1][0]
        if basis is None: nv=d
        else:
            U=torch.tensor(basis,dtype=r.dtype); nv=r+U@(U.T@(d-r))
        hr[layer-1]=nv[None,:]
        # continue through remaining visible tokens through FINAL; next output after FINAL predicts answer
        suffix=seq[rec:rec+1,pos+1:12]
        out,hs=model.continue_from(hr,suffix)
        if suffix.shape[1]==0:
            # state itself is after FINAL; read head directly
            pred=model.head(hr[-1])
        else: pred=out[:,-1]
        return int(pred.argmax(-1).item())

patch_rows=[]
for nm,pos in [('THINK',9),('CHECK',10),('FINAL',11)]:
 for li in range(1,model.layers+1):
    Ucmp=centroid_basis(acts[(li,nm)],labels['cmp'])
    for mode,basis in [('full',None),('cmp_subspace',Ucmp)]:
        ad=[]; ch=[]
        for i,j in pairs:
          for rec,don in [(i,j),(j,i)]:
            p=predict_after_patch(rec,don,li,pos,basis)
            ad.append(p==stoi[f'Y{meta.answer[don]}']); ch.append(p!=stoi[f'Y{meta.answer[rec]}'])
        patch_rows.append(dict(checkpoint=nm,layer=li,mode=mode,n=len(ad),donor_answer_adoption=float(np.mean(ad)),recipient_answer_change=float(np.mean(ch))))
patchdf=pd.DataFrame(patch_rows)

# 024: label-free future-control tomography.
# At a halt, derive PCA directions from hidden states only. Perturb one layer state and continue the SAME visible suffix.
# Signature = baseline answer logits + central finite-difference response along 6 PCA axes.
subidx=np.where(probe_test)[0][:120]
fmetrics=[]; fspec=[]
for nm,pos in [('THINK',9),('CHECK',10),('FINAL',11)]:
 for li in range(1,model.layers+1):
    Aall=acts[(li,nm)]; pca=PCA(n_components=6,random_state=SEED).fit(Aall[probe_train]); dirs=pca.components_; eps=.20
    S=[]; ids=[]
    for ii in subidx:
        with torch.no_grad(): base_states=model.state_after(seq[ii:ii+1,:pos+1])
        base=base_states[li-1][0].detach().clone(); responses=[]
        for delta in [torch.zeros_like(base)]+[sgn*eps*torch.tensor(d,dtype=base.dtype) for d in dirs for sgn in (1.,-1.)]:
            hs=[h.clone() for h in base_states]; hs[li-1]=(base+delta)[None,:]
            suffix=seq[ii:ii+1,pos+1:12]
            with torch.no_grad():
                if suffix.shape[1]: out,_=model.continue_from(hs,suffix); logits=out[0,-1,ans_ids]
                else: logits=model.head(hs[-1])[0,ans_ids]
            responses.append(logits.numpy())
        sig=list(responses[0])
        for q in range(6): sig.extend(((responses[1+2*q]-responses[2+2*q])/(2*eps)).tolist())
        S.append(sig); ids.append(ii)
    S=np.asarray(S); Sz=(S-S.mean(0))/(S.std(0)+1e-6)
    pc=PCA(n_components=min(10,len(S)-1,S.shape[1]),random_state=SEED).fit_transform(Sz)
    for target,k in [('cmp',3),('branch',5),('answer',5)]:
        km=KMeans(n_clusters=k,n_init=30,random_state=SEED).fit(pc)
        ami=adjusted_mutual_info_score(labels[target][ids],km.labels_)
        fmetrics.append(dict(checkpoint=nm,layer=li,target=target,k=k,AMI=float(ami)))
    svals=np.linalg.svd(Sz/np.sqrt(len(Sz)),compute_uv=False); e=svals*svals; fspec.append(dict(checkpoint=nm,layer=li,stable_rank=float(e.sum()/e.max()),d95=int(np.searchsorted(np.cumsum(e/e.sum()),.95)+1)))
fmetrics=pd.DataFrame(fmetrics); fspec=pd.DataFrame(fspec)

best={lab:probes[probes.label==lab].sort_values('accuracy',ascending=False).iloc[0].to_dict() for lab in labels}
bp=patchdf[patchdf['mode']=='cmp_subspace'].sort_values('donor_answer_adoption',ascending=False).iloc[0].to_dict(); bf=patchdf[patchdf['mode']=='full'].sort_values('donor_answer_adoption',ascending=False).iloc[0].to_dict()
bfind={t:fmetrics[fmetrics.target==t].sort_values('AMI',ascending=False).iloc[0].to_dict() for t in ['cmp','branch','answer']}
summary={'n_examples':len(meta),'answer_accuracy':answer_acc,'fixed_cot_accuracy':cot_acc,'layers':model.layers,'hidden_size':model.hid,'best_probes':best,'best_full_patch':bf,'best_cmp_subspace_patch':bp,'best_finder':bfind}
print(json.dumps(summary,indent=2,default=float),flush=True)

# save
meta.to_csv(OUT/'REASONING-LOCATOR-023_examples.csv',index=False); probes.to_csv(OUT/'REASONING-LOCATOR-023_probe_grid.csv',index=False); patchdf.to_csv(OUT/'REASONING-LOCATOR-023_activation_patching.csv',index=False); fmetrics.to_csv(OUT/'NATURAL-REASONING-FINDER-024_clustering.csv',index=False); fspec.to_csv(OUT/'NATURAL-REASONING-FINDER-024_spectrum.csv',index=False)
with open(OUT/'REASONING-LOCATOR-023_summary.json','w') as f: json.dump(summary,f,indent=2,default=float)
# figs
for lab in ['main','branch','cmp','answer','corrected']:
    plt.figure(figsize=(7,4))
    for nm in checkpoints:
        d=probes[(probes.label==lab)&(probes.checkpoint==nm)]; plt.plot(d.layer,d.accuracy,marker='o',label=nm)
    plt.ylim(0,1.03); plt.xlabel('GRU layer'); plt.ylabel('held-out probe accuracy'); plt.title(f'Where {lab} becomes readable'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/f'REASONING-LOCATOR-023_probe_{lab}.png',dpi=170); plt.close()
plt.figure(figsize=(7,4))
for mode in ['full','cmp_subspace']:
 d=patchdf[(patchdf.checkpoint=='CHECK')&(patchdf['mode']==mode)]; plt.plot(d.layer,d.donor_answer_adoption,marker='o',label=mode)
plt.ylim(0,1); plt.xlabel('patched GRU layer at CHECK halt'); plt.ylabel('donor-answer adoption'); plt.title('Causal transplant with identical visible CHECK token'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/'REASONING-LOCATOR-023_patching.png',dpi=170); plt.close()
plt.figure(figsize=(7,4))
for target in ['cmp','branch','answer']:
 d=fmetrics[fmetrics.target==target]; dd=d.groupby('layer').AMI.max(); plt.plot(dd.index,dd.values,marker='o',label=target)
plt.ylim(-.05,1); plt.xlabel('GRU layer'); plt.ylabel('AMI'); plt.title('Label-free future-control tomography, audited post hoc'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/'NATURAL-REASONING-FINDER-024_recovery.png',dpi=170); plt.close()

# reports
L=[]; A=L.append
A('# REASONING-LOCATOR-023 | 如果 CoT 不是思考过程，推理状态在模型哪里？'); A('')
A('## 研究设计'); A('')
A('使用三层自回归 GRU language model。6,400 个病例的 visible CoT 被故意锁死为同一串 `THINK → CHECK → FINAL`；这三个 token 不携带任何病例特异 main/branch/comparison 信息。prompt 给出 goal、start、两步 main plan 与两步 counterfactual plan；最终答案必须选择离 goal 更近的候选。因而模型若答对，只能把必要的 reasoning distinctions 保存在 prompt-conditioned internal state 中。')
A(f'训练完成：answer accuracy={answer_acc:.4f}；fixed-CoT token accuracy={cot_acc:.4f}。')
A('')
A('## 1. 停机点与逐层可读性'); A('')
A('在 SEP、THINK、CHECK、FINAL 四个时点真正停止 recurrent computation，保存三层 h_t；再用 held-out linear probe 审计 main candidate、counterfactual branch、comparison state、correction flag 与 final answer。')
for lab in ['main','branch','cmp','corrected','answer']:
 b=best[lab]; A(f'- {lab}: best accuracy={b["accuracy"]:.4f} at layer {int(b["layer"])} / {b["checkpoint"]}.')
A('可解码性只说明“这里有信息”，不单独作为推理因果证据。')
A('')
A('## 2. 同一可见 CoT token 下的 hidden-state transplant'); A('')
A('构造 donor/recipient 对：goal、start、main plan 完全相同，只改变 counterfactual plan；二者 visible CoT 仍完全相同，但 comparison 与答案不同。在 THINK/CHECK/FINAL 停机后，只替换一层 recurrent hidden state，再继续输入 recipient 原来的同一可见 suffix。')
A(f'- full hidden transplant 最强 donor-answer adoption={bf["donor_answer_adoption"]:.4f}，位置 {bf["checkpoint"]}/layer {int(bf["layer"])}。')
A(f'- 仅替换 comparison 三类 centroid 张成的 <=2D hidden subspace，最强 donor-answer adoption={bp["donor_answer_adoption"]:.4f}，位置 {bp["checkpoint"]}/layer {int(bp["layer"])}；recipient answer change={bp["recipient_answer_change"]:.4f}。')
A('这一干预保持 visible CoT token 不变，却让后续答案跟随 donor reasoning state，说明推理状态不是 CoT 字符本身，而是停机点的 internal predictive state。')
A('')
A('## 3. 推理“在哪里”的工作性定义'); A('')
A('本实验支持把 reasoning location 定义成 **model state × time × layer** 上满足三条条件的区域：① 能区分 future-equivalence classes；② 该处局部 future-response geometry 随 reasoning state 改变；③ transplant/低秩 patch 可因果改变后续轨迹。对 recurrent model，这个对象就是某个停机时刻的 hidden state；对 residual architectures，可对应 layer-position residual stream / KV state / recurrent memory 等同类 predictive state。')
A('')
A('## 4. 对 CoT 的结论'); A('')
A('CoT 可以是控制接口和外部工作记忆，但不等于完整 reasoning state。这里 CoT 字符串被严格固定，模型仍能形成不同 branch/comparison states；同一 CHECK token 下移植 hidden state 可以改变答案。因此“思考过程”至少有一部分存在于 token 之间/之下的状态动力学，而不是文本序列本身。')
(OUT/'REASONING-LOCATOR-023.md').write_text('\n'.join(L),encoding='utf8')

L=[]; A=L.append
A('# NATURAL-REASONING-FINDER-024 | 怎样在模型里找到类似自然推理的过程？'); A('')
A('## 核心思想'); A('')
A('真实 LLM 中没有 main/branch/compare 的真值标签。Finder 因而不从词义或预设 CoT 标签出发，而从 **停机后的未来可控性** 反推内部 reasoning states。')
A('')
A('## 1. Label-free future-control tomography'); A('')
A('在每个 layer/time checkpoint 停机。只用 hidden activation cloud 自身的 PCA 方向选 6 条局部扰动轴；沿每轴 ±ε 微扰 hidden state，再输入完全相同的 visible suffix，读取最终 answer logits。将 baseline logits 与六条 central finite-difference response 拼成 future-control signature。聚类完全不使用 latent reasoning labels。')
A('')
A('## 2. Synthetic audit'); A('')
for t in ['cmp','branch','answer']:
 b=bfind[t]; A(f'- 后验审计 {t}: best AMI={b["AMI"]:.4f} at {b["checkpoint"]}/layer {int(b["layer"])}。')
A('这些标签只在聚类完成后用于评价。在真实模型中可省略评价步骤，直接研究稳定出现的 future-control state classes。')
A('')
A('## 3. Natural Reasoning Finder 协议'); A('')
A('1. 收集 surface-equivalent checkpoints：相同/近似相同 token、相同当前答案读出，但不同上下文历史。')
A('2. 在 layer × time 网格停机，测 residual/hidden state。')
A('3. 对每个状态做 standardized future-control tomography：相同 suffix、局部扰动、future logits/Jacobian。')
A('4. 按 future-control signature 做 quotient/clustering，寻找“当前表面相同、未来控制不同”的隐藏类。')
A('5. silent branch test：找当前 output 不变、但 future signature 显著改变的内部方向。')
A('6. gate test：找 future-control geometry 发生分区或方向突变的位置，候选 comparison/selection gate。')
A('7. transplant test：跨病例移植整个 hidden state 或低维候选 subspace；若未来轨迹随 donor 改变，则建立因果身份。')
A('8. operator reconstruction：在发现的 state classes 之间拟合 state-dependent transitions，检查是否出现 memory/re-entry、branch、compare、correct 等与自然推理代数同构的操作，而不是要求它们具有相同文字名称。')
A('')
A('## 4. “像自然推理”的数学判据'); A('')
A('一个模型内部过程可被称为与本系列 natural-reasoning algebra 功能同构，当它同时出现：retained commitment、silent alternative branch、re-entry、future-based comparison partition、conditional correction，以及这些状态/算子可以由 future-equivalence + causal intervention 重建。它不要求显式输出人类式 CoT。')
(OUT/'NATURAL-REASONING-FINDER-024.md').write_text('\n'.join(L),encoding='utf8')

for prefix in ['REASONING-LOCATOR-023','NATURAL-REASONING-FINDER-024']:
 with zipfile.ZipFile(OUT/f'{prefix}_bundle.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in OUT.glob(f'{prefix}*'):
   if p.name.endswith('_bundle.zip'): continue
   z.write(p,p.name)
