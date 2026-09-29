import os,json,time,copy
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch import nn
import base_cg017 as base

R=Path(__file__).resolve().parent
OLD=R.parent/'cg017'
if (R/'reference_cg017').exists():OLD=R/'reference_cg017'
for p in ['models','predictions']: (R/p).mkdir(exist_ok=True)

def expand_truth():
    a=base.synthetic();rng=np.random.default_rng(17001);truth=[];all_y=[]
    for g in range(600):
        aa,b=rng.uniform(.25,.85,2)*rng.choice([-1,1],2)
        cov=np.array([[1,aa,aa*b],[aa,1,b],[aa*b,b,1.]])
        perm=rng.permutation(3);rng.multivariate_normal(np.zeros(3),cov,128)
        Bs=[]
        for o in range(3):
            B=np.zeros((3,3))
            if o==0:B[1,0]=aa;B[2,1]=b
            elif o==1:B[0,1]=aa;B[2,1]=b
            else:B[0,1]=aa;B[1,2]=b
            Bs.append(B[np.ix_(perm,perm)])
        q=int(rng.integers(3));s=int(rng.choice([j for j in range(3) if j!=q]))
        def effect(B,j):
            C=B.copy();C[j,:]=0;v=np.eye(3)[j]
            return np.linalg.solve(np.eye(3)-C,v)
        for B in Bs:
            C=B.copy();C[s,:]=0;v=1-(B**2).sum(1);v[s]=0;inv=np.linalg.inv(np.eye(3)-C)
            rng.multivariate_normal(effect(B,s),inv@np.diag(v)@inv.T/128)
            for present in [0,1]:truth.append(B);all_y.append(np.stack([effect(B,j) for j in range(3)]))
    a['true_B']=np.array(truth);a['all_query_truth']=np.array(all_y)
    assert np.allclose(a['y'],a['all_query_truth'][np.arange(len(a['y'])),a['query']])
    old=np.load(OLD/'synthetic_data.npz')
    assert np.array_equal(a['x'],old['x'])
    np.savez_compressed(R/'synthetic_data.npz',**a)
    return a

class MechanismModel(nn.Module):
    def __init__(self,task,mode):
        super().__init__();self.task=task;self.mode=mode;self.n=3 if task=='synthetic' else 11
        n=self.n;indim=15 if task=='synthetic' else 22
        self.enc=nn.Sequential(nn.Linear(indim,48),nn.Tanh(),nn.Linear(48,48),nn.Tanh())
        self.cell=nn.GRUCell(64,48)
        self.head=nn.Linear(48,3*n*n+3+(3*n if task=='real' else 0))
        zdim=3*n*n+3+(27 if task=='synthetic' else 6*n)
        self.project=nn.Linear(zdim,16)
        self.register_buffer('eye',torch.eye(n))
    def objects(self,h,x,edit=False):
        n=self.n;raw=self.head(h);B=torch.tanh(raw[:,:3*n*n]).reshape(-1,3,n,n)*(1-self.eye)
        B=.95*B/torch.maximum(B.abs().sum(-1,keepdim=True),torch.ones_like(B[...,:1]))
        logits=raw[:,3*n*n:3*n*n+3];w=logits.softmax(-1)
        if edit:
            B=B.clone();best=w.argmax(-1);flat=B[torch.arange(len(B)),best].abs().reshape(len(B),-1).argmax(-1)
            B[torch.arange(len(B)),best,flat//n,flat%n]*=-1
        if self.task=='synthetic':
            # axes: case, candidate, do-target, equation row, variable column
            mask=1-self.eye
            A=self.eye-B[:,:,None,:,:]*mask[None,None,:,:,None]
            rhs=self.eye[None,None,:,:].expand(len(B),3,-1,-1)
            sims=torch.linalg.solve(A,rhs[...,None]).squeeze(-1)
            q=x[:,-3:].argmax(-1);mus=sims[torch.arange(len(B))[:,None],torch.arange(3)[None,:],q[:,None]]
            p=torch.cat([mus.reshape(-1,9),logits],-1)
            offset=None
        else:
            offset=raw[:,3*n*n+3:].reshape(-1,3,n)
            m=x[:,n:];obs=x[:,:n];u=1-m
            A=self.eye-u[:,None,:,None]*B
            rhs=obs[:,None,:]+u[:,None,:]*offset
            sims=torch.linalg.solve(A,rhs[...,None]).squeeze(-1)
            p=(sims*w[:,:,None]).sum(1)
        return p,B,w,sims,offset
    def forward(self,x,cut=False,zero_effect=False,edge_flip=False,trace=False):
        e=self.enc(x[:,:15] if self.task=='synthetic' else x);h=e
        Bs=[];ps=[];ws=[];ss=[];tokens=[]
        for t in range(5):
            p,B,w,sims,b=self.objects(h,x,edit=edge_flip and t==1)
            if trace:Bs.append(B);ps.append(p);ws.append(w);ss.append(sims)
            if t==4:break
            parts=[B.flatten(1),w,sims.flatten(1)*(0 if zero_effect else 1)]
            if b is not None:parts.append(b.flatten(1))
            z=torch.tanh(self.project(torch.cat(parts,-1)))
            if self.mode=='mechanism_blank' or cut:z=z*0
            if trace:tokens.append(z)
            h=self.cell(torch.cat([e,z],-1),h)
        if trace:return p,{'B':torch.stack(Bs,1),'step_prediction':torch.stack(ps,1),'weights':torch.stack(ws,1),'simulations':torch.stack(ss,1),'tokens':torch.stack(tokens,1)}
        return p

def controls(model,x,y,mask,run):
    with torch.no_grad():
        p,tr=model(x,trace=True);rows=[];store={k:v[:32].numpy() for k,v in tr.items()}
        for name,kw in [('cut',{'cut':True}),('zero_effect',{'zero_effect':True}),('edge_flip',{'edge_flip':True}),('noop',{})]:
            pp,tt=model(x,trace=True,**kw);delta=base.expected(pp,model.task)-base.expected(p,model.task)
            if mask is not None:delta=delta*(1-mask)
            rows.append({'condition':name,'loss':float(base.loss(pp,y,model.task,mask)),'base_loss':float(base.loss(p,y,model.task,mask)),'prediction_rms':float((delta.square().sum()/(delta.numel() if mask is None else (1-mask).sum())).sqrt()),'next_B_rms':float((tt['B'][:,2]-tr['B'][:,2]).square().mean().sqrt())})
            store[name+'_step_prediction']=tt['step_prediction'][:32].numpy();store[name+'_B']=tt['B'][:32].numpy()
        np.savez_compressed(R/'predictions'/f'{run}_trace.npz',**store)
    return rows

def expanded_metrics(model,x,a,run):
    out=[]
    with torch.no_grad():
        for q in range(3):
            xx=x.clone();xx[:,-3:]=0;xx[:,-3+q]=1
            pred=model(xx);y=torch.tensor(a['all_query_truth'][:,q],dtype=torch.float32)
            out.append({'query':q,'loss':float(base.loss(pred,y,'synthetic')),'mse':float((base.expected(pred,'synthetic')-y).square().mean())})
        np.savez_compressed(R/'predictions'/f'{run}_all_queries.npz',**{f'query{q}':model(torch.cat([x[:,:15],torch.eye(3)[q].repeat(len(x),1)],1)).numpy() for q in range(3)})
    return out

def fit(task,mode,seed,fold,train,dev,test,meta,steps):
    torch.manual_seed(seed);rng=np.random.default_rng(seed+17000);model=MechanismModel(task,mode);opt=torch.optim.Adam(model.parameters(),lr=.002)
    x,y,m=train;vx,vy,vm=dev;tx,ty,tm=test;best=float('inf');logs=[];start=time.time()
    for step in range(1,steps+1):
        ix=rng.integers(len(x),size=96 if task=='synthetic' else 64)
        opt.zero_grad();l=base.loss(model(x[ix]),y[ix],task,None if m is None else m[ix]);l.backward();opt.step()
        if step%100==0:
            with torch.no_grad():vl=float(base.loss(model(vx),vy,task,vm))
            logs.append({'step':step,'train_loss':float(l.detach()),'dev_loss':vl})
            if vl<best:best=vl;chosen=step;state=copy.deepcopy(model.state_dict())
    model.load_state_dict(state);model.eval();run=f'{task}_{fold}_{mode}_{seed}'
    torch.save({'state_dict':state,'task':task,'mode':mode,'seed':seed,'fold':fold,'selected_step':chosen},R/'models'/f'{run}.pt')
    (R/'models'/f'{run}_training.json').write_text(json.dumps(logs))
    with torch.no_grad():p=model(tx)
    r={'task':task,'mode':mode,'seed':seed,'fold':fold,'dev_loss':best,'selected_step':chosen,'parameters':sum(v.numel() for v in model.parameters()),'seconds':time.time()-start}
    r.update(base.metrics(p,ty,task,tm,meta.get('worlds'),meta.get('support')))
    np.savez_compressed(R/'predictions'/f'{run}.npz',prediction=p.numpy())
    c=controls(model,tx,ty,tm,run) if mode=='mechanism_feedback' else []
    for row in c:row.update({'task':task,'mode':mode,'seed':seed,'fold':fold})
    expanded=[]
    if task=='synthetic':
        expanded=expanded_metrics(model,tx,meta['expanded'],run)
        for row in expanded:row.update({'mode':mode,'seed':seed})
        # Full synthetic trajectories support world-level illustrations.
        with torch.no_grad():_,tr=model(tx,trace=True)
        np.savez_compressed(R/'predictions'/f'{run}_full_trace.npz',**{k:v.numpy() for k,v in tr.items()})
    print(json.dumps(r),flush=True)
    return r,c,expanded

def main():
    a=expand_truth();splits=[]
    for s in range(3):
        ii=a['split']==s;splits.append((torch.tensor(a['x'][ii],dtype=torch.float32),torch.tensor(a['y'][ii],dtype=torch.float32),None))
    ii=a['split']==2;meta={'worlds':torch.tensor(a['worlds'][ii],dtype=torch.float32),'support':torch.tensor(a['support'][ii]),'expanded':{k:v[ii] for k,v in a.items()}}
    results=[];ctrl=[];expanded=[]
    def add(r,c,e):
        results.append(r);ctrl.extend(c);expanded.extend(e)
        pd.DataFrame(results).to_csv(R/'results.csv',index=False);pd.DataFrame(ctrl).to_csv(R/'mechanism_edits.csv',index=False);pd.DataFrame(expanded).to_csv(R/'all_query_results.csv',index=False)
    for seed in [11,22,33]:
        for mode in ['mechanism_blank','mechanism_feedback']:add(*fit('synthetic',mode,seed,'worlds',*splits,meta,1200))
    for fold,tr,dv,te,meta in base.real_folds():
        for seed in [11,22,33]:
            for mode in ['mechanism_blank','mechanism_feedback']:add(*fit('real',mode,seed,fold,tr,dv,te,meta,800))
    # Reuse all four frozen CG-017 models for expanded query evaluation.
    for seed in [11,22,33]:
        for mode in base.MODES:
            ck=torch.load(OLD/'models'/f'synthetic_worlds_{mode}_{seed}.pt',weights_only=True)
            model=base.Model(18,'synthetic',mode);model.load_state_dict(ck['state_dict']);model.eval()
            e=expanded_metrics(model,splits[2][0],{k:v[ii] for k,v in a.items()},f'synthetic_worlds_{mode}_{seed}')
            for row in e:row.update({'mode':mode,'seed':seed})
            expanded.extend(e)
    pd.DataFrame(expanded).to_csv(R/'all_query_results.csv',index=False)
    print('COMPLETE',flush=True)

if __name__=='__main__':main()
