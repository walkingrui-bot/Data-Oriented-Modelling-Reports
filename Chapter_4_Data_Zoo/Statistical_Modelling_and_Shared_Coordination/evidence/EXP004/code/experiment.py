import json, math, os, random, hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, r2_score

OUT = Path('/mnt/data/INTERNAL_COORDINATION_004')
OUT.mkdir(exist_ok=True)
(OUT/'results').mkdir(exist_ok=True)
(OUT/'states').mkdir(exist_ok=True)
(OUT/'figures').mkdir(exist_ok=True)

torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))

VIEW_NAMES = [
    'mean_size_shape', 'mean_irregularity',
    'se_size_shape', 'se_irregularity',
    'worst_size_shape', 'worst_irregularity'
]
VIEW_IDXS = [list(range(0,5)), list(range(5,10)), list(range(10,15)), list(range(15,20)), list(range(20,25)), list(range(25,30))]


def seed_all(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


def load_data(split_seed=42):
    d = load_breast_cancer()
    X = d.data.astype(np.float32); y = d.target.astype(np.int64)
    ids = np.arange(len(X))
    tr, te = train_test_split(ids, test_size=0.20, random_state=split_seed, stratify=y)
    views_tr=[]; views_te=[]; scalers=[]
    for idx in VIEW_IDXS:
        sc=StandardScaler().fit(X[tr][:,idx])
        views_tr.append(torch.tensor(sc.transform(X[tr][:,idx]),dtype=torch.float32))
        views_te.append(torch.tensor(sc.transform(X[te][:,idx]),dtype=torch.float32))
        scalers.append(sc)
    return d, tr, te, y[tr], y[te], views_tr, views_te, scalers

class RealityBindingNet(nn.Module):
    def __init__(self, d_in=5, hidden=32, core_dim=16):
        super().__init__()
        self.encoders=nn.ModuleList([nn.Sequential(nn.Linear(d_in,hidden),nn.Tanh(),nn.Linear(hidden,core_dim)) for _ in range(6)])
        self.core=nn.Linear(core_dim,core_dim)
        self.decoders=nn.ModuleList([nn.Sequential(nn.Linear(core_dim,hidden),nn.Tanh(),nn.Linear(hidden,d_in)) for _ in range(6)])
    def encode(self,x,view):
        h=self.encoders[view](x)
        return torch.tanh(self.core(h))
    def decode(self,z,view):
        return self.decoders[view](z)
    def all_latents(self,views):
        return [self.encode(views[i],i) for i in range(6)]


def derangement(n, rng):
    p=np.arange(n)
    while True:
        rng.shuffle(p)
        if np.all(p!=np.arange(n)):
            return p.copy()


def make_perms(n, seed):
    rng=np.random.default_rng(seed+12345)
    perms={}
    for i in range(6):
        for j in range(6):
            if i!=j:
                perms[(i,j)] = torch.tensor(derangement(n,rng),dtype=torch.long)
    return perms


def loss_all(model, views, mode='bind', perms=None, subset=None):
    if subset is None:
        xs=views
    else:
        xs=[v[subset] for v in views]
    zs=[model.encode(xs[i],i) for i in range(6)]
    losses=[]
    if mode=='self':
        for i in range(6):
            losses.append(torch.mean((model.decode(zs[i],i)-xs[i])**2))
    elif mode=='bind':
        zcat=torch.cat(zs,dim=0)
        for j in range(6):
            tgt=torch.cat([xs[j] for _ in range(6)],dim=0)
            losses.append(torch.mean((model.decode(zcat,j)-tgt)**2))
    elif mode=='shuffle':
        assert perms is not None and subset is None, 'shuffle uses full batch for fixed pairings'
        zcat=torch.cat(zs,dim=0)
        for j in range(6):
            tgts=[]
            for i in range(6):
                tgts.append(xs[j] if i==j else xs[j][perms[(i,j)]])
            tgt=torch.cat(tgts,dim=0)
            losses.append(torch.mean((model.decode(zcat,j)-tgt)**2))
    return torch.stack(losses).mean()


def train(model, views, steps, lr, mode, seed, perms=None, trace=False):
    opt=torch.optim.Adam(model.parameters(),lr=lr)
    n=len(views[0]); rng=np.random.default_rng(seed+999)
    trace_rows=[]
    batch=128
    for step in range(steps):
        opt.zero_grad(set_to_none=True)
        if mode=='shuffle':
            loss=loss_all(model,views,mode,perms=perms)
        else:
            idx=torch.tensor(rng.choice(n,size=min(batch,n),replace=False),dtype=torch.long)
            loss=loss_all(model,views,mode,subset=idx)
        loss.backward(); opt.step()
        if trace and (step<10 or (step+1)%25==0 or step==steps-1):
            trace_rows.append({'step':step+1,'loss':float(loss.detach())})
    return trace_rows


def pairwise_metrics(model, views):
    model.eval()
    with torch.no_grad():
        zs=[model.encode(views[i],i).cpu().numpy() for i in range(6)]
        rm=np.zeros((6,6),float)
        for i in range(6):
            z=torch.tensor(zs[i],dtype=torch.float32)
            for j in range(6):
                pred=model.decode(z,j).cpu().numpy()
                tgt=views[j].cpu().numpy()
                rm[i,j]=float(np.sqrt(np.mean((pred-tgt)**2)))
    diag=np.diag(rm); cross=rm[~np.eye(6,dtype=bool)]
    return zs, rm, float(diag.mean()), float(cross.mean())


def normalize_z(z, mu, sd):
    z=(z-mu)/sd
    norm=np.linalg.norm(z,axis=1,keepdims=True)+1e-12
    return z/norm


def retrieval_metrics(model, views_tr, views_te):
    model.eval()
    with torch.no_grad():
        ztr=[model.encode(views_tr[i],i).cpu().numpy() for i in range(6)]
        zte=[model.encode(views_te[i],i).cpu().numpy() for i in range(6)]
    # Shared normalization from all training views, not per-view alignment.
    pool=np.concatenate(ztr,axis=0)
    mu=pool.mean(0,keepdims=True); sd=pool.std(0,keepdims=True)+1e-6
    zteN=[normalize_z(z,mu,sd) for z in zte]
    acc=[]; top5=[]; pair_rows=[]
    n=len(zteN[0])
    for i in range(6):
        for j in range(6):
            if i==j: continue
            sims=zteN[i]@zteN[j].T
            pred=np.argmax(sims,axis=1)
            a=float(np.mean(pred==np.arange(n)))
            inds=np.argpartition(-sims, kth=min(4,n-1), axis=1)[:,:5]
            a5=float(np.mean([k in inds[k] for k in range(n)]))
            acc.append(a); top5.append(a5)
            pos=np.diag(sims)
            mask=~np.eye(n,dtype=bool)
            neg=sims[mask]
            pair_rows.append({'source':VIEW_NAMES[i],'target':VIEW_NAMES[j],'top1':a,'top5':a5,'positive_cos_mean':float(pos.mean()),'negative_cos_mean':float(neg.mean())})
    return float(np.mean(acc)), float(np.mean(top5)), pair_rows, zte


def latent_geometry(zs):
    # Shared standardized geometry using pooled latents.
    pool=np.concatenate(zs,axis=0)
    mu=pool.mean(0,keepdims=True); sd=pool.std(0,keepdims=True)+1e-6
    zn=[(z-mu)/sd for z in zs]
    n=zn[0].shape[0]
    same=[]
    for k in range(n):
        for i in range(6):
            for j in range(i+1,6):
                same.append(np.linalg.norm(zn[i][k]-zn[j][k])/math.sqrt(zn[i].shape[1]))
    return float(np.mean(same))


def label_audit(ztr, zte, ytr,yte):
    pool_tr=np.mean(np.stack(ztr,axis=1),axis=1)
    pool_te=np.mean(np.stack(zte,axis=1),axis=1)
    clf=LogisticRegression(max_iter=2000).fit(pool_tr,ytr)
    return float(accuracy_score(yte,clf.predict(pool_te)))


def gradient_pressure(model, views):
    model.zero_grad(set_to_none=True)
    loss=loss_all(model,views,'bind',subset=torch.arange(len(views[0])))
    loss.backward()
    groups={'encoder':[],'core':[],'decoder':[]}
    for name,p in model.named_parameters():
        if p.grad is None: continue
        key='encoder' if name.startswith('encoders') else ('core' if name.startswith('core') else 'decoder')
        groups[key].append(p.grad.detach().reshape(-1))
    out={}
    for k,gs in groups.items():
        g=torch.cat(gs); out[k+'_grad_rms']=float(torch.sqrt(torch.mean(g*g))); out[k+'_grad_norm']=float(torch.norm(g)); out[k+'_nparam']=int(g.numel())
    out['binding_loss']=float(loss.detach())
    return out


def first_step_displacement(model, views, lr=0.005):
    before={k:v.detach().clone() for k,v in model.state_dict().items()}
    opt=torch.optim.Adam(model.parameters(),lr=lr)
    opt.zero_grad(); loss=loss_all(model,views,'bind',subset=torch.arange(len(views[0]))); loss.backward(); opt.step()
    groups={'encoder':[],'core':[],'decoder':[]}
    for k,v in model.state_dict().items():
        if not torch.is_floating_point(v): continue
        d=(v-before[k]).reshape(-1)
        key='encoder' if k.startswith('encoders') else ('core' if k.startswith('core') else 'decoder')
        groups[key].append(d)
    return {k+'_delta_rms':float(torch.sqrt(torch.mean(torch.cat(ds)**2))) for k,ds in groups.items()}


def run_one(seed, condition, views_tr, views_te, ytr,yte, save=False):
    seed_all(seed)
    model=RealityBindingNet()
    perms=make_perms(len(views_tr[0]),seed)
    trace=[]; grad=None; disp=None
    if condition=='self_only':
        trace=train(model,views_tr,700,0.006,'self',seed,trace=save)
    elif condition=='direct_binding':
        trace=train(model,views_tr,900,0.005,'bind',seed,trace=save)
    elif condition=='switch_binding':
        train(model,views_tr,600,0.006,'self',seed)
        grad=gradient_pressure(model,views_tr)
        # clone for first displacement measurement, then restore exact pre-binding state
        st={k:v.detach().clone() for k,v in model.state_dict().items()}
        disp=first_step_displacement(model,views_tr,lr=0.005)
        model.load_state_dict(st)
        trace=train(model,views_tr,700,0.005,'bind',seed,trace=save)
    elif condition=='shuffled_pairing':
        train(model,views_tr,600,0.006,'self',seed)
        trace=train(model,views_tr,300,0.002,'shuffle',seed,perms=perms,trace=save)
    else: raise ValueError(condition)
    zte, rm, self_rmse,cross_rmse=pairwise_metrics(model,views_te)
    ret1,ret5,pairs,_=retrieval_metrics(model,views_tr,views_te)
    ztr=[model.encode(views_tr[i],i).detach().cpu().numpy() for i in range(6)]
    geo=latent_geometry(zte)
    lab=label_audit(ztr,zte,ytr,yte)
    row={'seed':seed,'condition':condition,'self_rmse':self_rmse,'cross_rmse':cross_rmse,'retrieval_top1':ret1,'retrieval_top5':ret5,'same_scene_latent_distance':geo,'diagnosis_audit_accuracy':lab}
    if grad: row.update(grad)
    if disp: row.update(disp)
    if save:
        torch.save(model.state_dict(),OUT/'states'/f'seed{seed}_{condition}.pt')
        pd.DataFrame(trace).to_csv(OUT/'results'/f'seed{seed}_{condition}_trace.csv',index=False)
        pd.DataFrame(rm,index=VIEW_NAMES,columns=VIEW_NAMES).to_csv(OUT/'results'/f'seed{seed}_{condition}_rmse_matrix.csv')
        pd.DataFrame(pairs).to_csv(OUT/'results'/f'seed{seed}_{condition}_retrieval_pairs.csv',index=False)
        np.savez_compressed(OUT/'results'/f'seed{seed}_{condition}_latents_test.npz',**{VIEW_NAMES[i]:zte[i] for i in range(6)})
    return row


def main():
    d,tr,te,ytr,yte,vtr,vte,sc=load_data()
    meta={'dataset':'sklearn.datasets.load_breast_cancer / Wisconsin Diagnostic Breast Cancer','n_total':len(d.data),'n_train':len(tr),'n_test':len(te),'features':d.feature_names.tolist(),'views':{VIEW_NAMES[i]:[d.feature_names[j] for j in VIEW_IDXS[i]] for i in range(6)},'core_dim':16,'split_seed':42}
    (OUT/'protocol.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    rows=[]
    for seed in [0,1,2,3,4]:
        for c in ['self_only','direct_binding','switch_binding','shuffled_pairing']:
            print('RUN',seed,c,flush=True)
            r=run_one(seed,c,vtr,vte,ytr,yte,save=(seed==0))
            print(r,flush=True); rows.append(r)
    df=pd.DataFrame(rows); df.to_csv(OUT/'results'/'all_runs.csv',index=False)
    summ=df.groupby('condition').agg(['median','mean','std'])
    summ.to_csv(OUT/'results'/'summary.csv')
    print('\nMEDIANS')
    print(df.groupby('condition')[['self_rmse','cross_rmse','retrieval_top1','retrieval_top5','same_scene_latent_distance','diagnosis_audit_accuracy']].median())
    # gradient/first update rows
    df[df.condition=='switch_binding'].to_csv(OUT/'results'/'switch_internal_change.csv',index=False)

if __name__=='__main__': main()
