#!/usr/bin/env python3
from pathlib import Path
import random, hashlib, json, zipfile
import numpy as np, pandas as pd
import torch, torch.nn as nn, torch.nn.functional as F
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, adjusted_mutual_info_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
OUT=Path('/mnt/data'); SEED=2304
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.set_num_threads(4)
N=5; OPS=['P1','P2','D2','NEG']
def ap(x,o): return {'P1':(x+1)%N,'P2':(x+2)%N,'D2':(2*x)%N,'NEG':(-x)%N}[o]
def di(x,g): d=(x-g)%N; return min(d,N-d)
def latent(g,x,m,c):
    main=ap(x,m); branch=ap(x,c); dm,db=di(main,g),di(branch,g); cmp=0 if db<dm else (1 if db==dm else 2); ans=branch if cmp==0 else main; return main,branch,cmp,ans,int(ans!=main)
TOK=['<BOS>','ALT','<SEP>','THINK','CHECK','FINAL','<EOS>']+[f'G{i}' for i in range(N)]+[f'X{i}' for i in range(N)]+OPS+[f'Y{i}' for i in range(N)]
stoi={t:i for i,t in enumerate(TOK)}; V=len(TOK)
seqs=[]; rows=[]
for g in range(N):
 for x in range(N):
  for m in OPS:
   for c in OPS:
    main,branch,cmp,ans,corr=latent(g,x,m,c)
    ts=['<BOS>',f'G{g}',f'X{x}',m,'ALT',c,'<SEP>','THINK','CHECK','FINAL',f'Y{ans}','<EOS>']
    seqs.append([stoi[t] for t in ts]); rows.append((g,x,m,c,main,branch,cmp,ans,corr))
seq=torch.tensor(seqs,dtype=torch.long); meta=pd.DataFrame(rows,columns=['goal','start','main_op','cf_op','main','branch','cmp','answer','corrected'])
probe_train=np.array([int(hashlib.sha1(str(r).encode()).hexdigest()[:8],16)%5!=0 for r in rows]); probe_test=~probe_train
class Model(nn.Module):
 def __init__(self):
  super().__init__(); self.emb=nn.Embedding(V,24); self.cells=nn.ModuleList([nn.GRUCell(24,48),nn.GRUCell(48,48),nn.GRUCell(48,48)]); self.head=nn.Linear(48,V); self.layers=3; self.hid=48
 def zero(self,B): return [torch.zeros(B,48) for _ in range(3)]
 def step(self,t,hs):
  x=self.emb(t); nh=[]
  for i,c in enumerate(self.cells): h=c(x,hs[i]); nh.append(h); x=h
  return self.head(nh[-1]),nh
 def forward(self,toks,ret=False):
  hs=self.zero(len(toks)); outs=[]; S=[[] for _ in range(3)]
  for q in range(toks.shape[1]):
   o,hs=self.step(toks[:,q],hs); outs.append(o)
   if ret:
    for l in range(3): S[l].append(hs[l])
  if ret: return torch.stack(outs,1),[torch.stack(s,1) for s in S],hs
  return torch.stack(outs,1)
 def state_after(self,toks):
  hs=self.zero(len(toks))
  for q in range(toks.shape[1]): _,hs=self.step(toks[:,q],hs)
  return [h.clone() for h in hs]
 def cont(self,hs,suf):
  out=[]
  for q in range(suf.shape[1]): o,hs=self.step(suf[:,q],hs); out.append(o)
  return (torch.stack(out,1) if out else None),hs
model=Model(); opt=torch.optim.AdamW(model.parameters(),lr=.01,weight_decay=1e-5)
# only final answer next-token objective after FINAL (input pos9); fixed CoT is teacher-forced and identical
for ep in range(500):
  lg=model(seq[:,:10]); target=seq[:,10]; loss=F.cross_entropy(lg[:,9],target)
  opt.zero_grad(); loss.backward(); opt.step()
  if ep%25==0:
   with torch.no_grad(): ac=(lg[:,9].argmax(-1)==target).float().mean().item()
   print(ep,loss.item(),ac,flush=True)
   if ac>.999: break
with torch.no_grad():
 lg,states,_=model(seq[:,:10],ret=True); pred=lg[:,9].argmax(-1).numpy(); answer_acc=float((pred==seq[:,10].numpy()).mean())
print('FINAL',answer_acc,flush=True)
torch.save({'state_dict':model.state_dict(),'vocab':TOK},OUT/'REASONING-LOCATOR-023_model.pt')
check={'SEP':6,'THINK':7,'CHECK':8,'FINAL':9}
acts={(l+1,n):states[l][:,p,:].numpy() for l in range(3) for n,p in check.items()}
labels={'main':meta.main.values,'branch':meta.branch.values,'cmp':meta.cmp.values,'answer':meta.answer.values,'corrected':meta.corrected.values}
pr=[]
for (l,n),A in acts.items():
 for lab,y in labels.items():
  clf=LogisticRegression(max_iter=1000,C=2.).fit(A[probe_train],y[probe_train]); a=accuracy_score(y[probe_test],clf.predict(A[probe_test])); pr.append((l,n,lab,a,1/len(np.unique(y))))
probes=pd.DataFrame(pr,columns=['layer','checkpoint','label','accuracy','chance'])
# matched pairs same goal/start/main op, different cf, answer+cmp differ
pairs=[]
for _,ids in meta.groupby(['goal','start','main_op']).groups.items():
 ids=list(ids)
 for i in range(len(ids)):
  for j in range(i+1,len(ids)):
   a,b=ids[i],ids[j]
   if meta.answer[a]!=meta.answer[b] and meta.cmp[a]!=meta.cmp[b]: pairs.append((a,b))
# comparison centroid bases
def cbasis(A,y):
 M=np.stack([A[probe_train&(y==c)].mean(0) for c in sorted(np.unique(y))]); M-=M.mean(0); _,s,v=np.linalg.svd(M,full_matrices=False); return v[:2].T

def patch_pred(rec,don,l,pos,U=None):
 with torch.no_grad():
  hr=model.state_after(seq[rec:rec+1,:pos+1]); hd=model.state_after(seq[don:don+1,:pos+1]); r=hr[l-1][0]; d=hd[l-1][0]
  if U is None: nv=d
  else:
   T=torch.tensor(U,dtype=r.dtype); nv=r+T@(T.T@(d-r))
  hr[l-1]=nv[None,:]; suf=seq[rec:rec+1,pos+1:10]; out,_=model.cont(hr,suf); zz=(out[0,-1] if suf.shape[1] else model.head(hr[-1])[0]); return int(zz.argmax())
patch=[]
for n,pos in [('THINK',7),('CHECK',8),('FINAL',9)]:
 for l in range(1,4):
  U=cbasis(acts[(l,n)],labels['cmp'])
  for mode,UU in [('full',None),('cmp_subspace',U)]:
   ad=[]; ch=[]
   for a,b in pairs:
    for rec,don in [(a,b),(b,a)]:
     p=patch_pred(rec,don,l,pos,UU); ad.append(p==stoi[f'Y{meta.answer[don]}']); ch.append(p!=stoi[f'Y{meta.answer[rec]}'])
   patch.append((n,l,mode,len(ad),np.mean(ad),np.mean(ch)))
patchdf=pd.DataFrame(patch,columns=['checkpoint','layer','mode','n','donor_answer_adoption','recipient_answer_change'])
# 024 label-free future-control tomography on all test states, perturb hidden along PCA dirs and continue same suffix
ansids=[stoi[f'Y{k}'] for k in range(N)]; fm=[]; fs=[]; testids=np.where(probe_test)[0]
for n,pos in [('THINK',7),('CHECK',8),('FINAL',9)]:
 for l in range(1,4):
  Aall=acts[(l,n)]; dirs=PCA(n_components=5,random_state=SEED).fit(Aall[probe_train]).components_; eps=.25; SS=[]
  for ii in testids:
   with torch.no_grad(): hs0=model.state_after(seq[ii:ii+1,:pos+1]); base=hs0[l-1][0].clone()
   resp=[]
   for delta in [torch.zeros_like(base)]+[sgn*eps*torch.tensor(d,dtype=base.dtype) for d in dirs for sgn in (1.,-1.)]:
    hs=[h.clone() for h in hs0]; hs[l-1]=(base+delta)[None,:]; suf=seq[ii:ii+1,pos+1:10]
    with torch.no_grad():
     out,_=model.cont(hs,suf); z=(out[0,-1] if suf.shape[1] else model.head(hs[-1])[0])[ansids].numpy()
    resp.append(z)
   sig=list(resp[0])
   for q in range(5): sig += list((resp[1+2*q]-resp[2+2*q])/(2*eps))
   SS.append(sig)
  S=np.array(SS); Z=(S-S.mean(0))/(S.std(0)+1e-6); pc=PCA(n_components=min(8,len(S)-1,S.shape[1]),random_state=SEED).fit_transform(Z)
  for target,k in [('cmp',3),('branch',5),('answer',5)]:
   lab=labels[target][testids]; km=KMeans(n_clusters=k,n_init=50,random_state=SEED).fit(pc); fm.append((n,l,target,adjusted_mutual_info_score(lab,km.labels_)))
  sv=np.linalg.svd(Z/np.sqrt(len(Z)),compute_uv=False); e=sv*sv; fs.append((n,l,e.sum()/e.max(),int(np.searchsorted(np.cumsum(e/e.sum()),.95)+1)))
fmetrics=pd.DataFrame(fm,columns=['checkpoint','layer','target','AMI']); fspec=pd.DataFrame(fs,columns=['checkpoint','layer','stable_rank','d95'])
best={lab:probes[probes.label==lab].sort_values('accuracy',ascending=False).iloc[0].to_dict() for lab in labels}; bf=patchdf[patchdf['mode']=='full'].sort_values('donor_answer_adoption',ascending=False).iloc[0].to_dict(); bp=patchdf[patchdf['mode']=='cmp_subspace'].sort_values('donor_answer_adoption',ascending=False).iloc[0].to_dict(); bfind={t:fmetrics[fmetrics.target==t].sort_values('AMI',ascending=False).iloc[0].to_dict() for t in ['cmp','branch','answer']}
summary={'n_examples':len(meta),'answer_accuracy':answer_acc,'fixed_visible_cot':'THINK CHECK FINAL','best_probes':best,'best_full_patch':bf,'best_cmp_subspace_patch':bp,'best_finder':bfind}
print(json.dumps(summary,indent=2,default=float),flush=True)
meta.to_csv(OUT/'REASONING-LOCATOR-023_examples.csv',index=False); probes.to_csv(OUT/'REASONING-LOCATOR-023_probe_grid.csv',index=False); patchdf.to_csv(OUT/'REASONING-LOCATOR-023_activation_patching.csv',index=False); fmetrics.to_csv(OUT/'NATURAL-REASONING-FINDER-024_clustering.csv',index=False); fspec.to_csv(OUT/'NATURAL-REASONING-FINDER-024_spectrum.csv',index=False); json.dump(summary,open(OUT/'REASONING-LOCATOR-023_summary.json','w'),indent=2,default=float)
# plots
for lab in ['main','branch','cmp','answer','corrected']:
 plt.figure(figsize=(7,4))
 for n in check: d=probes[(probes.label==lab)&(probes.checkpoint==n)]; plt.plot(d.layer,d.accuracy,'o-',label=n)
 plt.ylim(0,1.03); plt.xlabel('GRU layer'); plt.ylabel('probe accuracy'); plt.title(f'Internal readability: {lab}'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/f'REASONING-LOCATOR-023_probe_{lab}.png',dpi=160); plt.close()
plt.figure(figsize=(7,4))
for mode in ['full','cmp_subspace']:
 d=patchdf[(patchdf.checkpoint=='CHECK')&(patchdf['mode']==mode)]; plt.plot(d.layer,d.donor_answer_adoption,'o-',label=mode)
plt.ylim(0,1); plt.xlabel('layer'); plt.ylabel('donor-answer adoption'); plt.title('Hidden-state transplant at identical visible CHECK'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/'REASONING-LOCATOR-023_patching.png',dpi=160); plt.close()
plt.figure(figsize=(7,4))
for t in ['cmp','branch','answer']:
 d=fmetrics[fmetrics.target==t]; dd=d.groupby('layer').AMI.max(); plt.plot(dd.index,dd.values,'o-',label=t)
plt.ylim(-.05,1); plt.xlabel('layer'); plt.ylabel('AMI'); plt.title('Future-control tomography recovers latent reasoning states'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/'NATURAL-REASONING-FINDER-024_recovery.png',dpi=160); plt.close()
# reports
L=[]; A=L.append
A('# REASONING-LOCATOR-023 | CoT 不是完整思考过程时，推理状态在模型哪里？'); A(''); A('## 设计'); A('')
A('三层自回归 GRU 接收 goal/start/main relation/counterfactual relation。中间可见 CoT 被固定为同一个 teacher-forced 模板 `THINK → CHECK → FINAL`，对所有 400 个病例完全相同。最终 next-token answer 必须选择更接近 goal 的 main/branch 候选。于是表面 CoT 字符本身无法携带病例特异推理状态。')
A(f'最终 400/400 world answer accuracy = {answer_acc:.4f}。')
A(''); A('## 1. 逐层停机可读性')
for lab in ['main','branch','cmp','corrected','answer']:
 b=best[lab]; A(f'- {lab}: best held-out linear readout={b["accuracy"]:.4f}, at {b["checkpoint"]}/layer {int(b["layer"])}.')
A('线性可读性只标记“哪里存在信息”；因果身份由下一节 transplant 决定。')
A(''); A('## 2. 同一 visible CoT 下的 causal hidden transplant')
A('donor/recipient 保持 goal/start/main relation 相同，只改变 counterfactual relation；visible `THINK/CHECK/FINAL` 完全相同，但 comparison 与 answer 不同。模型在指定 token 后真正停机，只替换一层 recurrent hidden state，再继续喂 recipient 原来的相同 suffix。')
A(f'- full-state transplant: best donor-answer adoption={bf["donor_answer_adoption"]:.4f} at {bf["checkpoint"]}/layer {int(bf["layer"])}.')
A(f'- <=2D comparison-centroid subspace transplant: best donor-answer adoption={bp["donor_answer_adoption"]:.4f} at {bp["checkpoint"]}/layer {int(bp["layer"])}; recipient-answer change={bp["recipient_answer_change"]:.4f}.')
A('visible CoT 不变而 hidden-state transplant 改变未来输出，因此 reasoning state 至少部分位于 recurrent predictive state，而不是 CoT token identity。')
A(''); A('## 3. “推理在哪里”的数学判据')
A('定义 model reasoning locus 为 layer × time 上满足三条性质的 predictive state：① 可区分 future-equivalence classes；② 局部 future-response geometry 随 branch/compare state 变化；③ hidden-state 或低秩子空间干预可按 donor 状态因果重定向未来。对本 GRU，这个 locus 是可停机保存的 h_t；对 Transformer/SSM 可对应 residual/KV/recurrent state 的同类对象。')
A(''); A('## 4. CoT 的位置')
A('CoT 可以作为外部控制接口、时间刻度和工作记忆，但不是完整推理状态。这里 CoT 严格固定，内部仍形成不同 main/branch/comparison/correction states；所以“模型在想什么”必须从 hidden predictive dynamics 和 future-control geometry 看，而不能只读可见 CoT。')
(OUT/'REASONING-LOCATOR-023.md').write_text('\n'.join(L),encoding='utf8')
L=[]; A=L.append
A('# NATURAL-REASONING-FINDER-024 | 怎样在模型里寻找类似自然推理的内部过程？'); A(''); A('## 发现阶段不使用推理标签'); A('')
A('在每个 layer/time 停机，只从 hidden cloud 自身取 PCA 扰动方向；沿这些方向做 ±ε hidden perturbation，继续完全相同的 visible suffix，收集 answer logits 及 finite-difference future-control response。它们组成 future-control signature。聚类时不使用 main/branch/compare 真值。')
A(''); A('## Synthetic audit')
for t in ['cmp','branch','answer']:
 b=bfind[t]; A(f'- {t}: label-free clusters 与真值的最佳 post-hoc AMI={b["AMI"]:.4f}, at {b["checkpoint"]}/layer {int(b["layer"])}.')
A(''); A('## Natural Reasoning Finder 协议'); A('')
A('1. 收集 surface-equivalent checkpoints：当前 token/CoT/answer propensity 相同或近似，但历史不同。')
A('2. 在 layer × time 网格中暂停模型，保存 residual/hidden/KV state。')
A('3. 对每个状态做 standardized future-control tomography：相同 suffix + 局部 state perturbations + future logits/Jacobian。')
A('4. 按 future-control signature 建 future-equivalence quotient，而不是按 token 词义分类。')
A('5. 找 silent branch fiber：当前 readout 不变、future signature 改变。')
A('6. 找 comparison gate：future-control geometry 出现分区、方向突变或 conditional switch。')
A('7. 做 transplant/low-rank patch；只有能因果搬运未来行为的 internal class 才升级为 reasoning-state candidate。')
A('8. 在这些 state classes 之间拟合 operator algebra，检验是否出现 retained commitment、alternative branch、re-entry、comparison、conditional correction 等与自然推理功能同构的结构。')
A(''); A('## 判据')
A('“像自然推理”不要求模型输出人类式 CoT；要求模型内部存在与自然推理代数功能等价的 predictive distinctions，并能通过 future-equivalence 与因果干预恢复。')
(OUT/'NATURAL-REASONING-FINDER-024.md').write_text('\n'.join(L),encoding='utf8')
for pfx in ['REASONING-LOCATOR-023','NATURAL-REASONING-FINDER-024']:
 with zipfile.ZipFile(OUT/f'{pfx}_bundle.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in OUT.glob(pfx+'*'):
   if p.name.endswith('_bundle.zip'): continue
   z.write(p,p.name)
