from pathlib import Path
import copy, json, math, time
import numpy as np, pandas as pd
import torch
import run_cg022_engineered_world as core

ROOT=Path(__file__).resolve().parent
SEEDS=[11,22]

def query_nll_vec(B,lg,x,y):
    qs=x[:,-3:].argmax(-1); sims=[]
    for q in range(3): sims.append(core.apply_operator(B,{'type':'do','targets':[q],'values':[1.]}))
    S=torch.stack(sims,2)
    mus=S[torch.arange(len(B))[:,None],torch.arange(B.shape[1])[None,:],qs[:,None]]
    return core.mix_nll(mus,lg,y)

def support_obs_nll(B,lg,x):
    # support response in x[9:12], support target one-hot in x[12:15]
    qs=x[:,12:15].argmax(-1); sims=[]
    for q in range(3): sims.append(core.apply_operator(B,{'type':'do','targets':[q],'values':[1.]}))
    S=torch.stack(sims,2)
    mus=S[torch.arange(len(B))[:,None],torch.arange(B.shape[1])[None,:],qs[:,None]]
    return core.mix_nll(mus,lg,x[:,9:12])

def fit(seed,train,dev,test,steps=500):
    torch.manual_seed(seed); rng=np.random.default_rng(seed+2322); m=core.WorldProgram(core.K); opt=torch.optim.Adam(m.parameters(),lr=.0015)
    x,y,tb=train; vx,vy,vtb=dev; tx,ty,ttb,group,support=test
    best=1e9; state=None; logs=[]; t0=time.time()
    for step in range(1,steps+1):
        ix=rng.integers(len(x),size=64); xb=x[ix]; yb=y[ix]; tbb=tb[ix]; horizon=int(rng.integers(3,7))
        opt.zero_grad(); B,lg=m.form_world(xb,steps=horizon)
        orig=query_nll_vec(B,lg,xb,yb).mean()
        picks=rng.choice(len(core.TRAIN_SPECS),size=6,replace=False); bank=core.bank_loss(B,lg,tbb,[core.TRAIN_SPECS[j] for j in picks])
        supmask=xb[:,12:15].sum(-1)>0
        ev=torch.tensor(0.,dtype=orig.dtype); gain=torch.tensor(0.,dtype=orig.dtype)
        if supmask.any():
            post=support_obs_nll(B[supmask],lg[supmask],xb[supmask]).mean()
            xm=xb.clone(); xm[:,9:15]=0
            Bm,lm=m.form_world(xm,steps=horizon)
            masked=support_obs_nll(Bm[supmask],lm[supmask],xb[supmask]).mean()
            ev=post; gain=torch.relu(post-masked+0.05)
        loss=.40*orig+.40*bank+.10*ev+.10*gain
        loss.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),5);opt.step()
        if step%50==0:
            with torch.no_grad():
                Bv,lv=m.form_world(vx,steps=4); vo=query_nll_vec(Bv,lv,vx,vy).mean(); vb=core.bank_loss(Bv,lv,vtb,core.TRAIN_SPECS)
                vm=(.5*vo+.5*vb).item()
            logs.append({'step':step,'train_total':float(loss.detach()),'train_original':float(orig.detach()),'train_bank':float(bank.detach()),'train_evidence':float(ev.detach()),'train_gain_penalty':float(gain.detach()),'dev_original_nll':float(vo),'dev_operator_bank_nll':float(vb),'dev_balanced_score':vm,'horizon':horizon})
            if vm<best: best=vm; state=copy.deepcopy(m.state_dict()); sel=step
    m.load_state_dict(state);m.eval()
    metrics,detail,tr=core.evaluate(m,tx,ty,ttb,group,support,4)
    # paired support/no-support heldout bank benefit at group level
    d=detail[detail.bank=='heldout_bank'].groupby(['group','support']).nll.mean().unstack(); metrics['heldout_support_improvement']=float((d[0]-d[1]).mean())
    # evidence assimilation measurement against same model with support masked
    with torch.no_grad():
        Bf,lf=m.form_world(tx,steps=4); xm=tx.clone();xm[:,9:15]=0;Bm,lm=m.form_world(xm,steps=4)
        sm=torch.tensor(support.astype(bool)); post=support_obs_nll(Bf[sm],lf[sm],tx[sm]); pre=support_obs_nll(Bm[sm],lm[sm],tx[sm]); metrics['support_observation_nll_gain']=float((pre-post).mean()); metrics['support_observation_improved_rate']=float((post<pre).float().mean())
        # correct state sufficiency replay: saved t=2 state, continuation corresponds to global t=3-4 so support is visible immediately.
        _,_,a=m.form_world(tx,steps=2,trace=True); st=(a['B'][:,-1].clone(),a['logits'][:,-1].clone()); Br,Lr=m.form_world(tx,steps=2,start_state=st,reveal_step=1); B4,L4=m.form_world(tx,steps=4)
        metrics['state_replay_B_max_abs']=float((Br-B4).abs().max()); metrics['state_replay_logit_max_abs']=float((Lr-L4).abs().max())
    # 20-step rollout exact global evidence schedule: support hidden first two transitions, visible thereafter.
    curves=[];xc=tx[:200];tbc=ttb[:200];B=None;lg=None;prev=None
    with torch.no_grad():
        for h in range(1,21):
            B,lg=m.form_world(xc,steps=1,start_state=None if h==1 else (B,lg),reveal_step=(99 if h<3 else 1))
            curves.append({'seed':seed,'variant':'balanced','step':h,'heldout_bank_nll':float(core.bank_loss(B,lg,tbc,core.HELD_SPECS)),'B_step_rms':np.nan if prev is None else float((B-prev).square().mean().sqrt())});prev=B.clone()
    torch.save({'state_dict':state,'seed':seed,'selected_step':sel,'K':core.K},ROOT/'models'/f'balanced_{seed}.pt')
    (ROOT/'models'/f'balanced_{seed}_training.json').write_text(json.dumps(logs,indent=2))
    np.savez_compressed(ROOT/'predictions'/f'balanced_{seed}.npz',B=tr['B'].numpy(),logits=tr['logits'].numpy())
    return {'seed':seed,'variant':'balanced','parameters':sum(p.numel() for p in m.parameters()),'selected_step':sel,'dev_balanced_score':best,'seconds':time.time()-t0,**metrics},detail,pd.DataFrame(curves)

def main():
    torch.set_num_threads(4);z=np.load(core.DATA);spl=[]
    for s in range(3):
        ix=z['split']==s;spl.append((torch.tensor(z['x'][ix],dtype=torch.float32),torch.tensor(z['y'][ix],dtype=torch.float32),torch.tensor(z['true_B'][ix],dtype=torch.float32)))
    ix=z['split']==2;test=(*spl[2],z['group'][ix],z['support'][ix])
    res=[];det=[];cur=[]
    for seed in SEEDS:
        r,d,c=fit(seed,spl[0],spl[1],test);res.append(r);d['seed']=seed;d['variant']='balanced';det.append(d);cur.append(c);print(json.dumps(r),flush=True)
        pd.DataFrame(res).to_csv(ROOT/'balanced_results.csv',index=False);pd.concat(det,ignore_index=True).to_csv(ROOT/'balanced_operator_detail.csv',index=False);pd.concat(cur,ignore_index=True).to_csv(ROOT/'balanced_rollout.csv',index=False)
    print('COMPLETE',flush=True)
if __name__=='__main__':main()
