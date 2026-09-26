#!/usr/bin/env python3
from pathlib import Path
import math, random, json, argparse
import numpy as np, pandas as pd
import torch, torch.nn as nn, torch.nn.functional as F

apg=argparse.ArgumentParser(); apg.add_argument('--coverage',type=float,required=True); args=apg.parse_args()
OUT=Path('/mnt/data'); torch.set_num_threads(4)
N=5; OPS=['P1','P2','D2','NEG']
def ap(x,o): return {'P1':(x+1)%N,'P2':(x+2)%N,'D2':(2*x)%N,'NEG':(-x)%N}[o]
def di(x,g): d=(x-g)%N; return min(d,N-d)
def latent(g,x,m,c):
    main=ap(x,m); branch=ap(x,c); dm,db=di(main,g),di(branch,g); return main,branch,(branch if db<dm else main)
TOK=['<BOS>','ALT','<SEP>','THINK','CHECK','FINAL','<EOS>']+[f'G{i}' for i in range(N)]+[f'X{i}' for i in range(N)]+OPS+[f'Y{i}' for i in range(N)]
stoi={t:i for i,t in enumerate(TOK)}; V=len(TOK); yids=torch.tensor([stoi[f'Y{i}'] for i in range(N)])
seqs=[]; rows=[]
for g in range(N):
 for x in range(N):
  for mi,m in enumerate(OPS):
   for ci,c in enumerate(OPS):
    main,branch,ans=latent(g,x,m,c)
    ts=['<BOS>',f'G{g}',f'X{x}',m,'ALT',c,'<SEP>','THINK','CHECK','FINAL',f'Y{ans}','<EOS>']
    seqs.append([stoi[t] for t in ts]); rows.append((g,x,mi,ci,m,c,main,branch,ans))
SEQ=torch.tensor(seqs,dtype=torch.long); META=pd.DataFrame(rows,columns=['goal','start','main_i','cf_i','main_op','cf_op','main','branch','answer'])

def covmask(cov):
    k={0.25:1,0.5:2,1.0:4}[cov]; keep=[]
    for g,x,mi,ci,*_ in rows:
        base=(g*5+x+mi)%4; keep.append(ci in {(base+j)%4 for j in range(k)})
    return np.array(keep)
class LM(nn.Module):
    def __init__(self,hid,emb=16,layers=2):
        super().__init__(); self.hid=hid; self.layers=layers; self.emb=nn.Embedding(V,emb); self.gru=nn.GRU(emb,hid,layers,batch_first=True); self.head=nn.Linear(hid,V)
    def forward(self,toks,h0=None):
        o,h=self.gru(self.emb(toks),h0); return self.head(o),h
    def state(self,toks): return self.gru(self.emb(toks))[1]
    def cont(self,h,suf):
        if suf.shape[1]==0: return self.head(h[-1])[:,None,:],h
        o,h2=self.gru(self.emb(suf),h); return self.head(o),h2

def nparams(m): return sum(p.numel() for p in m.parameters())
def train(hid,cov,seed,maxep=900):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); m=LM(hid); ids=np.where(covmask(cov))[0]; tr=SEQ[ids,:10]; y=SEQ[ids,10]
    opt=torch.optim.AdamW(m.parameters(),lr=.012,weight_decay=1e-5); streak=0
    for ep in range(maxep):
        lg,_=m(tr); loss=F.cross_entropy(lg[:,9],y); opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(m.parameters(),5); opt.step()
        if ep%10==0:
            with torch.no_grad(): acc=(lg[:,9].argmax(-1)==y).float().mean().item()
            streak=streak+1 if acc>.999 else 0
            if streak>=3: break
    with torch.no_grad():
        lg,_=m(SEQ[:,:10]); pred=lg[:,9].argmax(-1); full=float((pred==SEQ[:,10]).float().mean()); trainacc=float((pred[ids]==SEQ[ids,10]).float().mean())
    return m,ids,dict(epochs=ep+1,train_acc=trainacc,full_acc=full,params=nparams(m),n_train=len(ids))

def analyze(m,info,hid,cov,seed):
    with torch.no_grad():
        h=m.state(SEQ[:,:9]); z,_=m.cont(h,SEQ[:,9:10]); yz=z[:,-1][:,yids]; pred=yz.argmax(-1).cpu().numpy(); truth=META.answer.values
    correct=np.where(pred==truth)[0]; H=m.layers*m.hid
    # full hidden batch, grad wrt state after CHECK
    h0=m.state(SEQ[correct,:9]).detach().requires_grad_(True); z,_=m.cont(h0,SEQ[correct,9:10]); yz=z[:,-1][:,yids]
    yy=torch.tensor(truth[correct]); vals=yz.detach(); tmp=vals.clone(); tmp[torch.arange(len(correct)),yy]=-1e9; runner=tmp.argmax(-1)
    margins=yz[torch.arange(len(correct)),yy]-yz[torch.arange(len(correct)),runner]
    g=torch.autograd.grad(margins.sum(),h0)[0]; gf=g.permute(1,0,2).reshape(len(correct),-1); hflat=h0.detach().permute(1,0,2).reshape(len(correct),-1)
    gnorm=gf.norm(dim=1); gain=gnorm*math.sqrt(H); lin=margins.detach()/(gain+1e-12)
    # vectorized exact radius along negative gradient (RMS units)
    dirs=(-gf/(gnorm[:,None]+1e-12)).reshape(len(correct),m.layers,m.hid).permute(1,0,2)
    def p_at(eps):
        # eps shape n, rms units
        hp=h0.detach()+dirs*(eps[None,:,None]*math.sqrt(H)); zz,_=m.cont(hp,SEQ[correct,9:10]); return zz[:,-1][:,yids].argmax(-1)
    base=yy; lo=torch.zeros(len(correct)); hi=torch.clamp(2.5*torch.clamp(lin.detach(),min=.02),min=.05,max=2.0)
    for _ in range(4):
        pr=p_at(hi); still=pr==base; hi=torch.where(still,torch.clamp(hi*1.8,max=4.0),hi)
    flippable=p_at(hi)!=base
    for _ in range(11):
        md=(lo+hi)/2; pr=p_at(md); same=pr==base; lo=torch.where(same,md,lo); hi=torch.where(same,hi,md)
    rad=torch.where(flippable,hi,torch.tensor(float('nan')))
    # crowding nearest different-answer distance in rms coordinates
    x=hflat.numpy(); a=truth[correct]; n=len(x); sq=(x*x).sum(1); dist2=(sq[:,None]+sq[None,:]-2*x@x.T)/H; dist2=np.maximum(dist2,0); dist=np.sqrt(dist2); dist[a[:,None]==a[None,:]]=np.inf; crowd=np.min(dist,axis=1)
    # spectrum gradients scaled for RMS perturbation
    G=(gf.detach().numpy()*math.sqrt(H)); s=np.linalg.svd(G/np.sqrt(len(G)),compute_uv=False); e=s*s; stable=float(e.sum()/e.max()); d95=int(np.searchsorted(np.cumsum(e/e.sum()),.95)+1)
    return dict(hidden=hid,coverage=cov,seed=seed,**info,n_correct=len(correct),median_margin=float(margins.median()),median_gain=float(gain.median()),median_linear_width=float(lin.median()),median_adv_width=float(torch.nanmedian(rad)),median_crowding=float(np.median(crowd)),control_stable_rank=stable,control_d95=d95)

cov=args.coverage; rowsout=[]
for hid in [64,128]:
 for seed in [2501,2502]:
    m,ids,info=train(hid,cov,seed); out=analyze(m,info,hid,cov,seed); rowsout.append(out); print('DONE',out,flush=True)
pd.DataFrame(rowsout).to_csv(OUT/f'MODEL-SCALE-CORRIDOR-025_cov{int(cov*100)}_tail.csv',index=False)
