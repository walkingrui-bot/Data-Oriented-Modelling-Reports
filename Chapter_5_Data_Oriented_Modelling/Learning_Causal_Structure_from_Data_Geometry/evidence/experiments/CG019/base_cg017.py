"""CG-017 reproducible CPU experiment. See protocol.md before interpreting results."""
import os, json, time, hashlib, copy, math
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch import nn
import torch.nn.functional as F

torch.set_num_threads(1)
torch.set_num_interop_threads(1)
ROOT=Path(__file__).resolve().parent
DATA=Path(os.environ.get('CG017_DATA_DIR',str(ROOT/'external_data')))
(ROOT/'models').mkdir(exist_ok=True)
(ROOT/'predictions').mkdir(exist_ok=True)
SEEDS=[11,22,33]
MODES=['direct','blank','continuous','structured']
SIGMA=.15

def synthetic():
    rng=np.random.default_rng(17001)
    arrays={k:[] for k in ['x','y','group','support','query','worlds','split']}
    for g in range(600):
        a,b=rng.uniform(.25,.85,2)*rng.choice([-1,1],2)
        cov=np.array([[1,a,a*b],[a,1,b],[a*b,b,1.]])
        perm=rng.permutation(3)
        obs=rng.multivariate_normal(np.zeros(3),cov,128)[:,perm]
        sample=np.cov(obs,rowvar=False)
        Bs=[]
        for orient in range(3):
            B=np.zeros((3,3))
            if orient==0: B[1,0]=a; B[2,1]=b
            elif orient==1: B[0,1]=a; B[2,1]=b
            else: B[0,1]=a; B[1,2]=b
            Bs.append(B[np.ix_(perm,perm)])
        q=int(rng.integers(3)); s=int(rng.choice([j for j in range(3) if j!=q]))
        def effect(B,j):
            C=B.copy(); C[j,:]=0
            v=np.zeros(3); v[j]=1
            return np.linalg.solve(np.eye(3)-C,v)
        ys=np.stack([effect(B,q) for B in Bs])
        for w,B in enumerate(Bs):
            # Support response sampled from the exact do-distribution.
            C=B.copy(); C[s,:]=0
            noisevar=1-np.square(B).sum(1); noisevar[s]=0
            inv=np.linalg.inv(np.eye(3)-C)
            scov=inv@np.diag(noisevar)@inv.T/128
            sr=rng.multivariate_normal(effect(B,s),scov)
            for present in [0,1]:
                x=np.r_[sample.ravel(),sr*present,np.eye(3)[s]*present,np.eye(3)[q]]
                for k,v in [('x',x),('y',ys[w]),('group',g),('support',present),('query',q),('worlds',ys),('split',0 if g<400 else 1 if g<500 else 2)]: arrays[k].append(v)
    arr={k:np.array(v) for k,v in arrays.items()}
    np.savez_compressed(ROOT/'synthetic_data.npz',**arr)
    return arr

class Model(nn.Module):
    def __init__(self,indim,task,mode):
        super().__init__(); self.task=task; self.mode=mode
        self.enc=nn.Sequential(nn.Linear(indim,48),nn.Tanh(),nn.Linear(48,48),nn.Tanh())
        self.cell=nn.GRUCell(64,48)
        self.latent=nn.Linear(48,16)
        self.head=nn.Linear(48,12 if task=='synthetic' else 11)
    def token(self,h,x):
        if self.mode=='continuous': return torch.tanh(self.latent(h))
        if self.mode=='structured':
            p=self.head(h)
            z=torch.cat([p[:,:9],p[:,9:].softmax(-1)],1) if self.task=='synthetic' else p*(1-x[:,11:])
            return F.pad(z,(0,16-z.shape[1]))
        return torch.zeros((len(x),16),device=x.device)
    def forward(self,x,cut=False,patch=None,trace=False):
        e=self.enc(x); h=e; tokens=[]; states=[h]; outputs=[self.head(h)]
        if self.mode!='direct':
            for t in range(4):
                z=self.token(h,x)
                if cut: z=z*0
                if patch is not None and t==1: z=patch
                tokens.append(z); h=self.cell(torch.cat([e,z],1),h)
                states.append(h); outputs.append(self.head(h))
        p=outputs[-1]
        if trace: return p,torch.stack(tokens,1),torch.stack(states,1),torch.stack(outputs,1)
        return p

def loss(p,y,task,mask=None):
    if task=='synthetic':
        mus=p[:,:9].reshape(-1,3,3); lp=p[:,9:].log_softmax(-1)
        logdensity=-.5*((mus-y[:,None,:])/SIGMA).square().sum(-1)-3*math.log(SIGMA*math.sqrt(2*math.pi))
        return -torch.logsumexp(lp+logdensity,1).mean()
    return ((p-y).square()*(1-mask)).sum()/(1-mask).sum()

def expected(p,task):
    if task=='synthetic': return (p[:,:9].reshape(-1,3,3)*p[:,9:].softmax(-1)[:,:,None]).sum(1)
    return p

def metrics(p,y,task,mask=None,worlds=None,support=None):
    r={'loss':float(loss(p,y,task,mask)), 'mse':float(((expected(p,task)-y).square() if mask is None else (expected(p,task)-y).square()*(1-mask)).sum()/(y.numel() if mask is None else (1-mask).sum()))}
    if task=='synthetic':
        mus=p[:,:9].reshape(-1,3,3); weight=p[:,9:].softmax(-1)
        r['best_candidate_mse']=float((mus-y[:,None,:]).square().mean(-1).min(1).values.mean())
        for v,name in [(0,'ambiguous'),(1,'support')]:
            idx=support==v
            r[name+'_nll']=float(loss(p[idx],y[idx],task))
            r[name+'_mean_mse']=float((expected(p[idx],task)-y[idx]).square().mean())
        idx=support==0
        # Candidate hit: RMS distance <=.20 and weight>=.10. Duplicate effects count equally by world.
        dist=(mus[idx,:,None,:]-worlds[idx,None,:,:]).square().mean(-1).sqrt()
        hits=((dist<=.20)&(weight[idx,:,None]>=.10)).any(1)
        r['ambiguous_world_coverage']=float(hits.float().mean())
    return r

def donor_indices(group):
    donor=np.arange(len(group))
    for g in np.unique(group):
        ix=np.flatnonzero(group==g); donor[ix]=np.roll(ix,1)
    return torch.tensor(donor)

def geometry(z):
    a=z.detach().numpy().reshape(-1,16); a=a-a.mean(0)
    ev=np.linalg.svd(a,compute_uv=False)**2
    if ev.sum()<1e-12:return {'token_participation_ratio':0.,'token_r95':0}
    return {'token_participation_ratio':float(ev.sum()**2/(ev**2).sum()),'token_r95':int(np.searchsorted(np.cumsum(ev)/ev.sum(),.95)+1)}

def interventions(model,x,y,task,mask,groups,runname):
    model.eval()
    with torch.no_grad():
        p,z,h,out=model(x,trace=True); donor=donor_indices(groups); transplant=z[donor,1].clone()
        rewrite=z[:,1].clone()
        if task=='real': rewrite[torch.arange(len(x)),mask.argmin(1)]+=1
        else: rewrite[:,0]+=1
        res=[]; arrays={'prediction':p.numpy(),'tokens':z.numpy(),'state':h.numpy(),'step_output':out.numpy(),'donor':donor.numpy(),'transplanted_token':transplant.numpy(),'rewritten_token':rewrite.numpy()}
        for name,kwargs in [('cut',{'cut':True}),('transplant',{'patch':transplant}),('rewrite',{'patch':rewrite}),('noop',{'patch':z[:,1]})]:
            pp,zz,_,oo=model(x,trace=True,**kwargs)
            delta=expected(pp,task)-expected(p,task)
            if mask is not None: delta=delta*(1-mask)
            res.append({'condition':name,'loss':float(loss(pp,y,task,mask)),'base_loss':float(loss(p,y,task,mask)), 'prediction_rms_shift':float((delta.square().sum()/(delta.numel() if mask is None else (1-mask).sum())).sqrt()),'next_token_rms_shift':float((zz[:,2]-z[:,2]).square().mean().sqrt())})
            arrays[name+'_prediction']=pp.numpy(); arrays[name+'_step_output']=oo.numpy()
        # Predetermined first eight cases; same original inputs, fixed token patches.
        xx=x[:8]; basepatch=z[:8,1]; otherpatch=transplant[:8]
        base=expected(model(xx,patch=basepatch),task); other=expected(model(xx,patch=otherpatch),task)
        j1=[];j2=[]
        for col in range(x.shape[1]//2 if task=='real' else 9):
            xeps=xx.clone(); xeps[:,col]+=.001
            j1.append((expected(model(xeps,patch=basepatch),task)-base)/.001)
            j2.append((expected(model(xeps,patch=otherpatch),task)-other)/.001)
        j1=torch.stack(j1,-1);j2=torch.stack(j2,-1)
        geom=geometry(z)
        geom.update({'input_sensitivity_relative_change':float((j1-j2).norm()/(j1.norm()+1e-9)), 'input_sensitivity_cosine':float(F.cosine_similarity(j1.flatten()[None,:],j2.flatten()[None,:]))})
        arrays['input_sensitivity_base']=j1.numpy(); arrays['input_sensitivity_transplant']=j2.numpy()
        if task=='real':
            arrays={k:(v[:32] if v.shape[0]==len(x) else v) for k,v in arrays.items()}
            arrays['trace_subset_indices']=np.arange(32)
        np.savez_compressed(ROOT/'predictions'/f'{runname}_trace.npz',**arrays)
    return res,geom

def fit(task,mode,seed,fold,train,dev,test,meta,steps):
    torch.manual_seed(seed); rng=np.random.default_rng(seed+17000)
    x,y,mask=train; vx,vy,vm=dev; tx,ty,tm=test
    model=Model(x.shape[1],task,mode)
    opt=torch.optim.Adam(model.parameters(),lr=.002)
    best=float('inf'); beststep=0; logs=[]; start=time.time()
    for step in range(1,steps+1):
        ix=rng.integers(len(x),size=96 if task=='synthetic' else 64)
        opt.zero_grad(); l=loss(model(x[ix]),y[ix],task,None if mask is None else mask[ix]); l.backward(); opt.step()
        if step%100==0:
            with torch.no_grad(): vl=float(loss(model(vx),vy,task,vm))
            logs.append({'step':step,'train_loss':float(l.detach()),'dev_loss':vl})
            if vl<best: best=vl;beststep=step;state=copy.deepcopy(model.state_dict())
    model.load_state_dict(state); model.eval()
    run=f'{task}_{fold}_{mode}_{seed}'
    torch.save({'state_dict':state,'task':task,'mode':mode,'seed':seed,'fold':fold,'input_dim':x.shape[1],'selected_step':beststep},ROOT/'models'/f'{run}.pt')
    (ROOT/'models'/f'{run}_training.json').write_text(json.dumps(logs))
    with torch.no_grad(): p=model(tx)
    r={'task':task,'fold':str(fold),'mode':mode,'seed':seed,'selected_step':beststep,'dev_loss':best,'parameters_total':sum(p.numel() for p in model.parameters()),'seconds':time.time()-start}
    active=['enc','head']+([] if mode=='direct' else ['cell'])+(['latent'] if mode=='continuous' else [])
    r['parameters_active']=sum(p.numel() for n,p in model.named_parameters() if n.split('.')[0] in active)
    r.update(metrics(p,ty,task,tm,meta.get('worlds'),meta.get('support')))
    payload={'prediction':p.detach().numpy()}
    if task=='synthetic':payload['truth']=ty.numpy()
    else:payload['mask']=tm.numpy()
    np.savez_compressed(ROOT/'predictions'/f'{run}.npz',**payload)
    ir=[]
    if mode in ['continuous','structured']:
        ir,geom=interventions(model,tx,ty,task,tm,meta['groups'],run);r.update(geom)
        for item in ir:item.update({'task':task,'fold':str(fold),'mode':mode,'seed':seed})
    print(json.dumps(r),flush=True)
    return r,ir

def real_folds():
    frame=pd.read_csv(DATA/'measurements.tsv',sep='\t'); manifest=pd.read_csv(DATA/'condition_manifest.csv')
    values=frame.iloc[:,1:].values.astype('float32'); rng=np.random.default_rng(17002)
    ids=[];conds=[];targets=[]
    for _,r in manifest.iterrows():
        if r['condition']=='cd3cd28' or pd.notna(r.intervention_target):
            ii=rng.choice(np.arange(r.start_row,r.stop_row),200,replace=False)
            ids.extend(ii);conds.extend([r['condition']]*200);targets.extend([r.intervention_target if pd.notna(r.intervention_target) else 'baseline']*200)
    ids=np.array(ids);conds=np.array(conds);targets=np.array(targets)
    pd.DataFrame({'source_row_zero_based':ids,'condition':conds,'target':targets}).to_csv(ROOT/'sachs_selection.csv',index=False)
    masks=np.ones((8,11),dtype='float32')
    for m in masks:m[rng.choice(11,5,replace=False)]=0
    np.save(ROOT/'mask_bank.npy',masks)
    isdev=np.zeros(len(ids),bool)
    for c in np.unique(conds): isdev[rng.choice(np.flatnonzero(conds==c),40,replace=False)]=True
    for target in ['akt','pkc','pip2','mek','pka']:
        tr=(targets!=target)&~isdev; dv=(targets!=target)&isdev; te=targets==target
        mean=values[ids[tr]].mean(0);std=values[ids[tr]].std(0);std=np.maximum(std,1e-6)
        standardized=(values[ids]-mean)/std
        splits=[]
        for select in [tr,dv,te]:
            y=np.repeat(standardized[select],8,axis=0); m=np.tile(masks,(int(select.sum()),1));x=np.c_[y*m,m]
            splits.append(tuple(torch.tensor(a,dtype=torch.float32) for a in [x,y,m]))
        # Store preprocessing and row ids, not external measurements.
        np.savez(ROOT/f'real_{target}_preprocessing.npz',mean=mean,std=std,train_rows=ids[tr],dev_rows=ids[dv],test_rows=ids[te])
        meta={'groups':np.tile(np.arange(8),int(te.sum()))}
        yield target,*splits,meta

def main():
    (ROOT/'runtime.json').write_text(json.dumps({'torch':torch.__version__,'numpy':np.__version__,'pandas':pd.__version__,'threads':1,'seeds':SEEDS,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())},indent=2))
    a=synthetic(); splits=[]
    for s in range(3):
        idx=a['split']==s;splits.append((torch.tensor(a['x'][idx],dtype=torch.float32),torch.tensor(a['y'][idx],dtype=torch.float32),None))
    idx=a['split']==2;meta={'worlds':torch.tensor(a['worlds'][idx],dtype=torch.float32),'support':torch.tensor(a['support'][idx]),'groups':a['query'][idx]*2+a['support'][idx]}
    results=[];controls=[]
    def add(r,c):
        results.append(r);controls.extend(c)
        pd.DataFrame(results).to_csv(ROOT/'results.csv',index=False);pd.DataFrame(controls).to_csv(ROOT/'feedback_interventions.csv',index=False)
    for seed in SEEDS:
        for mode in MODES:add(*fit('synthetic',mode,seed,'worlds',*splits,meta,1200))
    for target,tr,dv,te,meta in real_folds():
        for seed in SEEDS:
            for mode in MODES:add(*fit('real',mode,seed,target,tr,dv,te,meta,800))
    print('COMPLETE',flush=True)

if __name__=='__main__':main()
