import os, math, json, copy
import numpy as np, pandas as pd
import torch
from torch import nn
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
os.makedirs(f'{ROOT}/results',exist_ok=True); os.makedirs(f'{ROOT}/data',exist_ok=True); os.makedirs(f'{ROOT}/figures',exist_ok=True)
torch.set_num_threads(1)

# Reuse the exact stable channel/world scaffold from Experiment 005 without running its experiment loops.
code=open(os.path.join(os.path.dirname(__file__),'base_scaffold.py')).read()
ns={'__file__':os.path.join(os.path.dirname(__file__),'base_scaffold.py')}; exec(code,ns)
Model=ns['Model']; Y_base=ns['Y_base']; X=ns['X']; tr_idx=ns['tr_idx']; te_idx=ns['te_idx']; bind_loss=ns['bind_loss']; channelize=ns['channelize']

# One auditable physiological direction derived only from the training backbone.
Xtr=X[tr_idx]
_,_,vt=np.linalg.svd(Xtr-Xtr.mean(0,keepdims=True),full_matrices=False)
WORLD_DIR=vt[0].astype(np.float32); WORLD_DIR/=np.linalg.norm(WORLD_DIR)+1e-8

T=12; CHANGE=4

def ramp():
    r=np.zeros(T,np.float32)
    r[CHANGE:]=np.linspace(0,1,T-CHANGE,dtype=np.float32)
    return r
RAMP=ramp()

def stable_views(Xseq):
    # Baseline measurement mechanisms from 005. Noise is deterministic for a given shape.
    return channelize(np.asarray(Xseq,np.float32),False)

def apply_dynamic_drift(y5, d, shape='train'):
    # A changing measurement state applied *after* the stable assay mechanism.
    # It does not change the latent patient/world state.
    y=np.asarray(y5,np.float32); d=np.asarray(d,np.float32)[:,None]
    off=np.linspace(-0.20,0.22,y.shape[1],dtype=np.float32)[None,:]
    if shape=='train':
        z=(1+0.34*d)*y + d*off + 0.09*d*np.tanh(1.7*y)
    else: # held-out drift shape: stronger nonlinear calibration curve
        z=(1+0.28*d)*y + 0.85*d*off + 0.08*d*np.sin(2.2*y) + 0.035*d*(y*y)*np.sign(y)
    return np.clip(z,-4,4).astype(np.float32)

def make_episode(idx, kind, rng, drift_shape='train'):
    x0=X[idx].copy()
    sign=np.float32(rng.choice([-1.0,1.0]))
    if kind in ('world','both'):
        w=sign*RAMP
    else:
        w=np.zeros(T,np.float32)
    if kind in ('drift','both'):
        d=RAMP.copy()
    else:
        d=np.zeros(T,np.float32)
    # modest real-state displacement along a training-derived data direction
    Xseq=x0[None,:] + (0.72*w[:,None])*WORLD_DIR[None,:]
    Y=stable_views(Xseq) # T x 6 x 10
    if np.any(d):
        Y[:,5,:]=apply_dynamic_drift(Y[:,5,:],d,drift_shape)
    return Y.astype(np.float32), w.astype(np.float32), d.astype(np.float32)

def build_episodes(ids, seed, drift_shape='train'):
    rng=np.random.default_rng(seed)
    kinds=['none','drift','world','both']
    Ys=[]; Ws=[]; Ds=[]; Ks=[]; Base=[]
    # one episode of each kind per person keeps the design balanced
    for idx in ids:
        for k in kinds:
            y,w,d=make_episode(int(idx),k,rng,drift_shape)
            Ys.append(y);Ws.append(w);Ds.append(d);Ks.append(k);Base.append(int(idx))
    return np.stack(Ys),np.stack(Ws),np.stack(Ds),np.array(Ks),np.array(Base)

class DynamicChannelState(nn.Module):
    """Shared recurrent channel-state estimator + small channel-specific correction heads.
    It sees only each channel's deviation from the current cross-channel consensus.
    """
    def __init__(self,state_dim=8):
        super().__init__(); self.state_dim=state_dim
        self.gru=nn.GRUCell(16,state_dim)
        self.in_heads=nn.ModuleList([nn.Linear(state_dim,16) for _ in range(6)])
        self.out_heads=nn.ModuleList([nn.Linear(state_dim,16) for _ in range(6)])
        for h in list(self.in_heads)+list(self.out_heads):
            nn.init.zeros_(h.weight);nn.init.zeros_(h.bias)

    def forward_sequence(self,base,Y):
        # Y: B,T,6,10. Stable base model is frozen.
        B,T_,C,D=Y.shape
        s=torch.zeros(B,C,self.state_dim,device=Y.device)
        preds=[]; realities=[]; states=[]; candidates=[]
        for t in range(T_):
            yt=Y[:,t]
            hs=[]
            for c in range(C):
                h=base.perc(yt[:,c,:]); h=base.cin[c](h); hs.append(h)
            H=torch.stack(hs,dim=1) # B,C,16
            consensus=H.mean(dim=1,keepdim=True)
            dev=H-consensus
            new=[]
            for c in range(C):
                new.append(self.gru(dev[:,c,:],s[:,c,:]))
            s=torch.stack(new,dim=1)
            zc=[]
            for c in range(C):
                dh=0.30*torch.tanh(self.in_heads[c](s[:,c,:]))
                zc.append(torch.tanh(base.core(H[:,c,:]+dh)))
            Z=torch.stack(zc,dim=1)
            r=Z.mean(dim=1)
            out=[]
            for c in range(C):
                dz=0.30*torch.tanh(self.out_heads[c](s[:,c,:]))
                out.append(base.gen(base.cout[c](r+dz)))
            preds.append(torch.stack(out,dim=1)); realities.append(r); states.append(s); candidates.append(Z)
        return torch.stack(preds,dim=1),torch.stack(realities,dim=1),torch.stack(states,dim=1),torch.stack(candidates,dim=1)

class StatelessConsensus(nn.Module):
    def forward_sequence(self,base,Y):
        B,T_,C,D=Y.shape;preds=[];realities=[];states=[];cands=[]
        for t in range(T_):
            yt=Y[:,t]; zc=[]
            for c in range(C):
                h=base.perc(yt[:,c,:]);h=base.cin[c](h);zc.append(torch.tanh(base.core(h)))
            Z=torch.stack(zc,1);r=Z.mean(1);out=[]
            for c in range(C):out.append(base.gen(base.cout[c](r)))
            preds.append(torch.stack(out,1));realities.append(r);cands.append(Z);states.append(torch.zeros(B,C,8,device=Y.device))
        return torch.stack(preds,1),torch.stack(realities,1),torch.stack(states,1),torch.stack(cands,1)

def train_base(seed,steps=300):
    torch.manual_seed(seed);np.random.seed(seed);rng=np.random.default_rng(seed+1234)
    m=Model('neural');opt=torch.optim.Adam(m.parameters(),lr=0.008)
    for step in range(steps):
        ids=rng.choice(tr_idx,size=64,replace=False);b=torch.tensor(Y_base[ids],dtype=torch.float32)
        opt.zero_grad();loss=bind_loss(m,b);loss.backward();opt.step()
    for p in m.parameters(): p.requires_grad=False
    return m

def train_state(base,seed,Ytr,steps=450):
    torch.manual_seed(seed+100); np.random.seed(seed+100);rng=np.random.default_rng(seed+5000)
    st=DynamicChannelState(8);opt=torch.optim.Adam(st.parameters(),lr=0.006)
    traj=[];n=len(Ytr)
    for step in range(steps):
        ix=rng.choice(n,size=min(32,n),replace=False)
        b=torch.tensor(Ytr[ix],dtype=torch.float32)
        opt.zero_grad();pred,r,s,z=st.forward_sequence(base,b)
        mse=((pred-b)**2).mean()
        # keep dynamic state economical and smooth; no event labels or latent alignment targets
        reg=2e-4*(s*s).mean()+2e-4*((s[:,1:]-s[:,:-1])**2).mean()
        loss=mse+reg;loss.backward();opt.step()
        if step in [0,24,99,224,449]:traj.append((step+1,float(mse.item()),float(reg.item())))
    return st,traj

def category_rmse(pred,Y,kinds):
    out={}
    for k in ['none','drift','world','both']:
        m=np.where(kinds==k)[0]
        out[k]=float(np.sqrt(np.mean((pred[m]-Y[m])**2)))
    return out

def eval_system(base,router,Y,W,D,K):
    with torch.no_grad():
        yt=torch.tensor(Y,dtype=torch.float32)
        pred,R,S,Z=router.forward_sequence(base,yt)
    pred=pred.numpy();R=R.numpy();S=S.numpy();Z=Z.numpy()
    rmses=category_rmse(pred,Y,K)
    # focused RMSE for channel 5, plus other channels
    focus={};other={}
    for k in ['none','drift','world','both']:
        m=np.where(K==k)[0]
        focus[k]=float(np.sqrt(np.mean((pred[m,:,5,:]-Y[m,:,5,:])**2)))
        other[k]=float(np.sqrt(np.mean((pred[m,:,:5,:]-Y[m,:,:5,:])**2)))
    # dynamic state energy by channel and category
    energy=np.linalg.norm(S,axis=-1) # E,T,C
    state={}
    for k in ['none','drift','world','both']:
        m=np.where(K==k)[0]
        state[k]=energy[m].mean(axis=(0,1))
    # reality movement from episode baseline
    dR=np.linalg.norm(R-R[:,0:1,:],axis=-1)
    worldmove={k:float(dR[K==k,-1].mean()) for k in ['none','drift','world','both']}
    # probes: true world coefficient from delta reality; true drift from c5 state
    featsR=(R-R[:,0:1,:]).reshape(-1,16); targW=W.reshape(-1)
    featsS=S[:,:,5,:].reshape(-1,S.shape[-1]); targD=D.reshape(-1)
    return dict(pred=pred,R=R,S=S,Z=Z,rmses=rmses,focus=focus,other=other,state=state,worldmove=worldmove,featsR=featsR,targW=targW,featsS=featsS,targD=targD)

def fit_probe(trainX,trainy,testX,testy):
    rg=Ridge(alpha=1.0).fit(trainX,trainy);p=rg.predict(testX);return float(r2_score(testy,p))

def run_seed(seed=0):
    base=train_base(seed)
    Ytr,Wtr,Dtr,Ktr,_=build_episodes(tr_idx,20261001+seed,'train')
    Yte,Wte,Dte,Kte,Bte=build_episodes(te_idx,303000+seed,'test')
    st,traj=train_state(base,seed,Ytr)
    ev=eval_system(base,st,Yte,Wte,Dte,Kte)
    nost=eval_system(base,StatelessConsensus(),Yte,Wte,Dte,Kte)
    # train-side features for probes
    etr=eval_system(base,st,Ytr,Wtr,Dtr,Ktr)
    world_r2=fit_probe(etr['featsR'],etr['targW'],ev['featsR'],ev['targW'])

    # Paired state audit: every person has [none, drift, world, both] in this order.
    # Subtracting the no-change episode removes each channel's stable baseline state.
    def paired(E,W,D):
        n=E['S'].shape[0]//4
        S=E['S'].reshape(n,4,T,6,-1); R=E['R'].reshape(n,4,T,16)
        W4=W.reshape(n,4,T); D4=D.reshape(n,4,T)
        dS_drift=S[:,1]-S[:,0]; dS_world=S[:,2]-S[:,0]
        dR_drift=R[:,1]-R[:,0]; dR_world=R[:,2]-R[:,0]
        return dS_drift,dS_world,dR_drift,dR_world,W4,D4
    tr_dSd,tr_dSw,tr_dRd,tr_dRw,W4tr,D4tr=paired(etr,Wtr,Dtr)
    te_dSd,te_dSw,te_dRd,te_dRw,W4te,D4te=paired(ev,Wte,Dte)
    drift_r2=fit_probe(tr_dSd[:,:,5,:].reshape(-1,8),D4tr[:,1,:].reshape(-1),
                       te_dSd[:,:,5,:].reshape(-1,8),D4te[:,1,:].reshape(-1))
    drift_energy=np.linalg.norm(te_dSd,axis=-1).mean(axis=(0,1))
    world_state_energy=np.linalg.norm(te_dSw,axis=-1).mean(axis=(0,1))
    loc_ratio=float((drift_energy[5]+1e-8)/(np.mean(drift_energy[:5])+1e-8))
    world_state_crosstalk=float(np.mean(world_state_energy))
    drift_state5=float(drift_energy[5])
    drift_reality_move=float(np.linalg.norm(te_dRd[:,-1,:],axis=-1).mean())
    world_reality_move=float(np.linalg.norm(te_dRw[:,-1,:],axis=-1).mean())
    reality_ratio=float((world_reality_move+1e-8)/(drift_reality_move+1e-8))
    row={
        'seed':seed,'world_probe_r2':world_r2,'drift_probe_r2':drift_r2,
        'drift_state_localization_ratio':loc_ratio,'world_state_crosstalk':world_state_crosstalk,
        'drift_state5_energy':drift_state5,'reality_world_to_drift_move_ratio':reality_ratio,'paired_reality_drift_move':drift_reality_move,'paired_reality_world_move':world_reality_move,
    }
    for k,v in ev['rmses'].items():row[f'state_rmse_{k}']=v
    for k,v in nost['rmses'].items():row[f'nostate_rmse_{k}']=v
    for k,v in ev['focus'].items():row[f'state_c5_rmse_{k}']=v
    for k,v in nost['focus'].items():row[f'nostate_c5_rmse_{k}']=v
    for k,v in ev['worldmove'].items():row[f'reality_move_{k}']=v
    for c in range(6):
        row[f'state_energy_drift_c{c}']=float(drift_energy[c]);row[f'state_energy_world_c{c}']=float(world_state_energy[c])
    # save seed0 arrays/trajectories
    if seed==0:
        np.savez_compressed(f'{ROOT}/results/seed0_dynamic_arrays.npz',Y=Yte,W=Wte,D=Dte,kinds=Kte,base_ids=Bte,pred=ev['pred'],R=ev['R'],S=ev['S'],Z=ev['Z'])
        pd.DataFrame(traj,columns=['step','mse','state_reg']).to_csv(f'{ROOT}/results/seed0_training_trajectory.csv',index=False)
        torch.save(base.state_dict(),f'{ROOT}/results/seed0_frozen_base.pt')
        torch.save(st.state_dict(),f'{ROOT}/results/seed0_dynamic_state.pt')
    return row

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=0);args=ap.parse_args()
    row=run_seed(args.seed);print(json.dumps(row,indent=2))
