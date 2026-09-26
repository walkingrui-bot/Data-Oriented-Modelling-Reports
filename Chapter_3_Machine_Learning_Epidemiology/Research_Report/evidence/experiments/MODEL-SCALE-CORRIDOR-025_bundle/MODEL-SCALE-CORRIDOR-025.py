#!/usr/bin/env python3
from pathlib import Path
import math, random, json, hashlib, zipfile, time
import numpy as np, pandas as pd
import torch, torch.nn as nn, torch.nn.functional as F
import matplotlib.pyplot as plt

OUT=Path('/mnt/data')
torch.set_num_threads(4)
BASE_SEED=2501
N=5; OPS=['P1','P2','D2','NEG']
def ap(x,o): return {'P1':(x+1)%N,'P2':(x+2)%N,'D2':(2*x)%N,'NEG':(-x)%N}[o]
def di(x,g): d=(x-g)%N; return min(d,N-d)
def latent(g,x,m,c):
    main=ap(x,m); branch=ap(x,c); dm,db=di(main,g),di(branch,g)
    ans=branch if db<dm else main
    return main,branch,ans
TOK=['<BOS>','ALT','<SEP>','THINK','CHECK','FINAL','<EOS>']+[f'G{i}' for i in range(N)]+[f'X{i}' for i in range(N)]+OPS+[f'Y{i}' for i in range(N)]
stoi={t:i for i,t in enumerate(TOK)}; V=len(TOK); YIDS=torch.tensor([stoi[f'Y{i}'] for i in range(N)])
seqs=[]; rows=[]
for g in range(N):
 for x in range(N):
  for mi,m in enumerate(OPS):
   for ci,c in enumerate(OPS):
    main,branch,ans=latent(g,x,m,c)
    ts=['<BOS>',f'G{g}',f'X{x}',m,'ALT',c,'<SEP>','THINK','CHECK','FINAL',f'Y{ans}','<EOS>']
    seqs.append([stoi[t] for t in ts]); rows.append((g,x,mi,ci,m,c,main,branch,ans))
SEQ=torch.tensor(seqs,dtype=torch.long)
META=pd.DataFrame(rows,columns=['goal','start','main_i','cf_i','main_op','cf_op','main','branch','answer'])

# Balanced nested coverage subsets: every (goal,start,main_op) group exists; cf coverage grows 1->2->4.
def coverage_mask(level):
    keep=[]
    k={0.25:1,0.5:2,1.0:4}[level]
    for r in rows:
        g,x,mi,ci,*_=r
        base=(g*5+x+mi)%4
        allowed={(base+j)%4 for j in range(k)}
        keep.append(ci in allowed)
    return np.array(keep)

class LM(nn.Module):
    def __init__(self,hid,emb=16,layers=2):
        super().__init__(); self.hid=hid; self.layers=layers
        self.emb=nn.Embedding(V,emb)
        self.gru=nn.GRU(emb,hid,num_layers=layers,batch_first=True)
        self.head=nn.Linear(hid,V)
    def forward(self,toks,h0=None):
        e=self.emb(toks); o,h=self.gru(e,h0); return self.head(o),h,o
    def prefix_state(self,toks):
        e=self.emb(toks); o,h=self.gru(e); return h
    def continue_from(self,h,suf):
        if suf.shape[1]==0:
            z=self.head(h[-1])[:,None,:]; return z,h
        e=self.emb(suf); o,h2=self.gru(e,h); return self.head(o),h2

def nparams(m): return sum(p.numel() for p in m.parameters())

def train_one(hid,cov,seed,max_epochs=1000):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    m=LM(hid)
    mask=coverage_mask(cov); ids=np.where(mask)[0]
    tr=SEQ[ids,:10]; y=SEQ[ids,10]
    opt=torch.optim.AdamW(m.parameters(),lr=0.012,weight_decay=1e-5)
    best=0; streak=0; last_loss=None
    for ep in range(max_epochs):
        lg,_,_=m(tr); loss=F.cross_entropy(lg[:,9],y)
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(m.parameters(),5.0); opt.step()
        if ep%10==0 or ep==max_epochs-1:
            with torch.no_grad(): acc=(lg[:,9].argmax(-1)==y).float().mean().item()
            best=max(best,acc); last_loss=float(loss)
            if acc>0.999: streak+=1
            else: streak=0
            if streak>=3: break
    with torch.no_grad():
        lg,_,_=m(SEQ[:,:10]); pred=lg[:,9].argmax(-1); full_acc=float((pred==SEQ[:,10]).float().mean())
        tr_acc=float((pred[ids]==SEQ[ids,10]).float().mean())
    return m, {'epochs':ep+1,'train_acc':tr_acc,'full_acc':full_acc,'loss':last_loss,'n_train':len(ids),'params':nparams(m)}

def future_logits_from_h(m,h,idx,pos=8):
    # state after CHECK (pos 8), continue with FINAL (pos9), read next-token logits
    suf=SEQ[idx:idx+1,pos+1:10]
    z,_=m.continue_from(h,suf)
    return z[0,-1,YIDS]

def analyze_one(m,traininfo,cov,hid,seed,max_cases=160):
    # states after CHECK for whole world
    with torch.no_grad():
        h=m.prefix_state(SEQ[:,:9]) # after CHECK at pos8
        z,_=m.continue_from(h,SEQ[:,9:10]); yz=z[:,-1][:,YIDS]
        pred_class=yz.argmax(-1).numpy(); truth=META.answer.values
    correct=np.where(pred_class==truth)[0]
    # deterministic subsample across all answers
    if len(correct)>max_cases:
        rng=np.random.default_rng(seed+99); correct=np.sort(rng.choice(correct,max_cases,replace=False))
    records=[]; grads=[]; flatstates=[]
    H=m.layers*m.hid
    for idx in correct:
        h0=m.prefix_state(SEQ[idx:idx+1,:9]).detach().requires_grad_(True)
        logits=future_logits_from_h(m,h0,idx)
        y=int(META.answer.iloc[idx]); vals=logits.detach().numpy(); runner=int(np.argsort(vals)[-2]) if int(np.argmax(vals))==y else int(np.argmax(vals))
        margin=logits[y]-logits[runner]
        g=torch.autograd.grad(margin,h0,retain_graph=False)[0]
        gv=g.detach().reshape(-1); gnorm=float(gv.norm())
        gain_rms=gnorm*math.sqrt(H)
        rlin=float(margin.detach())/(gain_rms+1e-12)
        # exact steepest descent radius along -gradient, RMS units; binary search if flip occurs
        d=(-gv/(gv.norm()+1e-12)).reshape_as(h0)
        base_pred=int(logits.argmax())
        def pp(eps_rms):
            hp=(h0.detach()+d*(eps_rms*math.sqrt(H)))
            with torch.no_grad(): return int(future_logits_from_h(m,hp,idx).argmax())
        lo=0.0; hi=max(0.02,min(2.0,2.5*max(rlin,0.02)))
        while hi<4.0 and pp(hi)==base_pred: hi*=1.6
        if pp(hi)==base_pred:
            rad=np.nan
        else:
            for _ in range(16):
                md=(lo+hi)/2
                if pp(md)==base_pred: lo=md
                else: hi=md
            rad=hi
        # random direction median radius, 4 dirs
        rng=np.random.default_rng(seed*100000+idx)
        rr=[]
        for _ in range(4):
            dv=torch.tensor(rng.normal(size=H),dtype=h0.dtype); dv=dv/(dv.norm()+1e-12); dv=dv.reshape_as(h0)
            a=0.0; b=0.1
            while b<4.0:
                hp=h0.detach()+dv*(b*math.sqrt(H))
                with torch.no_grad(): pr=int(future_logits_from_h(m,hp,idx).argmax())
                if pr!=base_pred: break
                b*=1.7
            if b>=4.0: rr.append(np.nan); continue
            for _ in range(12):
                md=(a+b)/2; hp=h0.detach()+dv*(md*math.sqrt(H))
                with torch.no_grad(): pr=int(future_logits_from_h(m,hp,idx).argmax())
                if pr==base_pred: a=md
                else: b=md
            rr.append(b)
        records.append((idx,float(margin.detach()),gain_rms,rlin,rad,float(np.nanmedian(rr))))
        grads.append(gv.numpy()*math.sqrt(H)) # normalized to RMS input units
        flatstates.append(h0.detach().reshape(-1).numpy())
    rdf=pd.DataFrame(records,columns=['idx','answer_margin','future_gain_rms','linear_width','adversarial_width','random_width'])
    # crowding over all correct states, RMS hidden distance to closest state with different answer
    # hidden coordinates are tanh-comparable; normalize RMS per coordinate.
    hs=m.prefix_state(SEQ[correct,:9]).detach().permute(1,0,2).reshape(len(correct),-1).numpy()
    ans=META.answer.values[correct]; n=len(correct); crowd=[]
    if n>1:
        # block-wise to save memory
        for i in range(n):
            dif=hs-hs[i]; dist=np.sqrt(np.mean(dif*dif,axis=1)); dist[ans==ans[i]]=np.inf
            crowd.append(np.min(dist))
    # control spectrum: gradient matrix across correct sampled states
    G=np.stack(grads) if grads else np.zeros((1,H)); s=np.linalg.svd(G/np.sqrt(len(G)),compute_uv=False); e=s*s
    stable=float(e.sum()/e.max()) if e.max()>0 else 0.0
    d95=int(np.searchsorted(np.cumsum(e/e.sum()),.95)+1) if e.sum()>0 else 0
    out=dict(hidden=hid,coverage=cov,seed=seed,**traininfo,
             n_correct_analyzed=len(rdf),
             median_margin=float(rdf.answer_margin.median()) if len(rdf) else np.nan,
             median_gain=float(rdf.future_gain_rms.median()) if len(rdf) else np.nan,
             median_linear_width=float(rdf.linear_width.median()) if len(rdf) else np.nan,
             median_adv_width=float(rdf.adversarial_width.median()) if rdf.adversarial_width.notna().any() else np.nan,
             median_random_width=float(rdf.random_width.median()) if rdf.random_width.notna().any() else np.nan,
             median_crowding=float(np.median(crowd)) if crowd else np.nan,
             control_stable_rank=stable,control_d95=d95)
    return out,rdf

WIDTHS=[8,16,32,64,128]
COVS=[0.25,0.5,1.0]
SEEDS=[2501,2502]
summary=[]; detail=[]
for cov in COVS:
 for hid in WIDTHS:
  for seed in SEEDS:
   m,ti=train_one(hid,cov,seed)
   out,rd=analyze_one(m,ti,cov,hid,seed)
   summary.append(out); rd['hidden']=hid; rd['coverage']=cov; rd['seed']=seed; detail.append(rd)
   print('DONE',cov,hid,seed,out['train_acc'],out['full_acc'],out['median_adv_width'],out['median_crowding'],out['control_stable_rank'],flush=True)
S=pd.DataFrame(summary); D=pd.concat(detail,ignore_index=True)
S.to_csv(OUT/'MODEL-SCALE-CORRIDOR-025_models.csv',index=False); D.to_csv(OUT/'MODEL-SCALE-CORRIDOR-025_cases.csv',index=False)
# aggregate by condition
agg=S.groupby(['coverage','hidden']).agg(params=('params','mean'),train_acc=('train_acc','mean'),full_acc=('full_acc','mean'),adv_width=('median_adv_width','mean'),random_width=('median_random_width','mean'),margin=('median_margin','mean'),gain=('median_gain','mean'),crowding=('median_crowding','mean'),stable_rank=('control_stable_rank','mean'),d95=('control_d95','mean')).reset_index()
agg.to_csv(OUT/'MODEL-SCALE-CORRIDOR-025_aggregate.csv',index=False)
# derived correlations across all trained models
corr=S[['params','n_train','full_acc','median_adv_width','median_random_width','median_margin','median_gain','median_crowding','control_stable_rank']].corr(method='spearman')
corr.to_csv(OUT/'MODEL-SCALE-CORRIDOR-025_spearman.csv')
# plots
for metric,title,ylabel,fn in [
 ('full_acc','Generalization accuracy vs model size','Full-world accuracy','MODEL-SCALE-CORRIDOR-025_accuracy.png'),
 ('adv_width','Adversarial trajectory-corridor width','Hidden perturbation RMS to answer flip','MODEL-SCALE-CORRIDOR-025_width.png'),
 ('crowding','Predictive-state separation','Nearest different-answer hidden RMS distance','MODEL-SCALE-CORRIDOR-025_crowding.png'),
 ('gain','Future-control gain','Worst-direction logit gain per hidden RMS','MODEL-SCALE-CORRIDOR-025_gain.png'),
 ('stable_rank','Control-direction diversity','Stable rank of stacked answer gradients','MODEL-SCALE-CORRIDOR-025_rank.png')]:
 plt.figure(figsize=(7,4.5))
 for cov in COVS:
  d=agg[agg.coverage==cov]; plt.plot(d.hidden,d[metric],'o-',label=f'{int(cov*100)}% unique coverage')
 plt.xscale('log',base=2); plt.xlabel('Hidden width'); plt.ylabel(ylabel); plt.title(title); plt.legend(); plt.tight_layout(); plt.savefig(OUT/fn,dpi=170); plt.close()
# simple 2D relation plot width vs accuracy
plt.figure(figsize=(6.5,4.5));
for cov in COVS:
 d=agg[agg.coverage==cov]; plt.plot(d.adv_width,d.full_acc,'o-',label=f'{int(cov*100)}% coverage')
plt.xlabel('Adversarial corridor width'); plt.ylabel('Full-world accuracy'); plt.title('Answer accuracy vs corridor width'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/'MODEL-SCALE-CORRIDOR-025_width_vs_accuracy.png',dpi=170); plt.close()

# Report
lines=[]; A=lines.append
A('# MODEL-SCALE-CORRIDOR-025 | 模型大小、训练覆盖与“正确道路宽度”')
A('')
A('## 研究问题')
A('固定同一个 400-case reasoning universe、相同表面 token 系统、相同固定 CoT 模板与同一 answer objective，只改变模型 hidden width 与训练集 unique coverage。目标不是问“大模型方向盘更多吗”，而是把“正确道路宽/窄”写成可测量的 hidden-state robustness corridor，并同时读取 accuracy、future gain、state crowding 与 control-rank。')
A('')
A('## 操作性定义')
A('- trajectory corridor width：在 CHECK 后冻结完整 recurrent state，沿最陡 answer-margin 下降方向扰动，继续完全相同的 FINAL suffix；使最终 answer 首次改变所需的最小 per-coordinate RMS perturbation。')
A('- random corridor width：四个随机 hidden directions 上的翻转半径中位数。')
A('- future-control gain：answer margin 对完整 recurrent state 的梯度范数，换算成每单位 hidden RMS perturbation 的最坏方向增益。')
A('- state crowding：正确病例中，每个 CHECK state 到最近“不同最终答案” state 的 hidden RMS 距离。')
A('- control stable rank：跨病例堆叠 answer-margin gradients 后的 SVD stable rank；用于区分“道路变宽”与“方向数量增加”。')
A('')
A('## 主结果表（两 seed 均值）')
A('```')
A(agg.to_string(index=False,float_format=lambda x:f'{x:.4f}'))
A('```')
A('')
# derive prominent patterns programmatically
full=agg[agg.coverage==1.0].sort_values('hidden')
A('## 结果与现场讨论')
A(f'- 在 100% coverage 下，hidden width 从 {int(full.hidden.iloc[0])} 增至 {int(full.hidden.iloc[-1])} 时，full-world accuracy 从 {full.full_acc.iloc[0]:.3f} 到 {full.full_acc.iloc[-1]:.3f}；adversarial corridor width 从 {full.adv_width.iloc[0]:.4f} 到 {full.adv_width.iloc[-1]:.4f}；不同答案 state 的最近距离从 {full.crowding.iloc[0]:.4f} 到 {full.crowding.iloc[-1]:.4f}。')
A(f'- 同一条件下 control stable rank 从 {full.stable_rank.iloc[0]:.3f} 到 {full.stable_rank.iloc[-1]:.3f}。因此模型变大是否主要表现为“控制自由度增多”可以和“同一控制结构被摊开/变宽”直接分开检查。')
for cov in COVS:
 d=agg[agg.coverage==cov].sort_values('hidden'); A(f'- {int(cov*100)}% coverage：width {int(d.hidden.iloc[0])}→{int(d.hidden.iloc[-1])} 时 accuracy {d.full_acc.iloc[0]:.3f}→{d.full_acc.iloc[-1]:.3f}，corridor {d.adv_width.iloc[0]:.4f}→{d.adv_width.iloc[-1]:.4f}，crowding distance {d.crowding.iloc[0]:.4f}→{d.crowding.iloc[-1]:.4f}。')
A('')
A('## 数学 picture')
A('模型大小不直接等价于 reasoning-control dimension。更一般地可把训练后状态流形写成 M_theta = phi_theta(Z_teacher)。teacher/training data 决定需要表达的 predictive distinctions；architecture capacity 决定 phi_theta 能否把这些 distinctions 在 ambient hidden space 中分开。道路宽度可写成局部鲁棒半径 r(h)=inf{||delta||_RMS : argmax A(h+delta) != argmax A(h)}。当 r 增大而 control rank 不同比例增加时，更符合“geometric unpacking / corridor widening”而不是“增加更多方向盘”。')
A('')
A('## 原始数据')
for f in ['MODEL-SCALE-CORRIDOR-025_models.csv','MODEL-SCALE-CORRIDOR-025_cases.csv','MODEL-SCALE-CORRIDOR-025_aggregate.csv','MODEL-SCALE-CORRIDOR-025_spearman.csv','MODEL-SCALE-CORRIDOR-025_accuracy.png','MODEL-SCALE-CORRIDOR-025_width.png','MODEL-SCALE-CORRIDOR-025_crowding.png','MODEL-SCALE-CORRIDOR-025_gain.png','MODEL-SCALE-CORRIDOR-025_rank.png','MODEL-SCALE-CORRIDOR-025_width_vs_accuracy.png']:
 A(f'- {f}')
(OUT/'MODEL-SCALE-CORRIDOR-025.md').write_text('\n'.join(lines),encoding='utf8')
# zip
with zipfile.ZipFile(OUT/'MODEL-SCALE-CORRIDOR-025_bundle.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.glob('MODEL-SCALE-CORRIDOR-025*'):
        if p.name.endswith('_bundle.zip'): continue
        z.write(p,p.name)
print('FINISHED')
