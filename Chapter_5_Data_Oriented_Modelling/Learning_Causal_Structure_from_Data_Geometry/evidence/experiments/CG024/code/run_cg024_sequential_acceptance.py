from pathlib import Path
import sys, json, copy, time
import numpy as np, pandas as pd, torch
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import run_cg023_coordinate_world as cg
D,K=cg.D,cg.K
OUT=Path('/mnt/data/cg024_final/CAUSAL_GEOMETRY_024')
OUT.mkdir(parents=True,exist_ok=True); (OUT/'models').mkdir(exist_ok=True); (OUT/'figures').mkdir(exist_ok=True)
SEEDS=[11,22]

def make_context(rng,w,eqbank,tmbank,n=8):
    pres=int(rng.integers(0,3))
    if pres==0:
        pick=rng.choice(16,n,replace=False); c=eqbank[w,pick]; k=np.zeros(n,np.int64)
    elif pres==1:
        pick=rng.choice(16,n,replace=False); c=tmbank[w,pick]; k=np.ones(n,np.int64)
    else:
        ne=n//2; pe=rng.choice(16,ne,replace=False); pt=rng.choice(16,n-ne,replace=False)
        c=np.concatenate([eqbank[w,pe],tmbank[w,pt]],0); k=np.r_[np.zeros(ne,np.int64),np.ones(n-ne,np.int64)]
    o=rng.permutation(n); return c[o].astype('float32'),k[o]

def rollout_event_np(M,b,x0,h,typ,j,val,tau):
    x=x0.astype('float32').copy(); bc=b.astype('float32').copy()
    for t in range(h):
        if t==tau:
            if typ==0: x[j]+=val
            elif typ==1: x[j]=val
            else: bc[j]+=val
        x=M@x+bc
    return x.astype('float32')

def rollout_events_np(M,b,x0,h,events):
    x=x0.astype('float32').copy(); bc=b.astype('float32').copy()
    for t in range(h):
        for typ,j,val,tau in events:
            if t==tau:
                if typ==0: x[j]+=val
                elif typ==1: x[j]=val
                else: bc[j]+=val
        x=M@x+bc
    return x.astype('float32')

def exec_event_torch(M,b,x0,h,typ,j,val,tau):
    B,Kk=M.shape[:2]; x=x0[:,None,:].expand(B,Kk,D).clone(); bc=b.clone(); out=torch.zeros_like(x)
    for t in range(int(h.max())):
        ids=torch.where(tau==t)[0]
        for ii in ids.tolist():
            jj=int(j[ii]); vv=val[ii]
            if int(typ[ii])==0: x[ii,:,jj]=x[ii,:,jj]+vv
            elif int(typ[ii])==1: x[ii,:,jj]=vv
            else: bc[ii,:,jj]=bc[ii,:,jj]+vv
        x=torch.einsum('bkij,bkj->bki',M,x)+bc
        done=(h==(t+1))
        if done.any(): out[done]=x[done]
    return out

def exec_two_events_torch(M,b,x0,h,ev1,ev2):
    B,Kk=M.shape[:2]; x=x0[:,None,:].expand(B,Kk,D).clone(); bc=b.clone(); out=torch.zeros_like(x)
    for t in range(int(h.max())):
        for ev in (ev1,ev2):
            ids=torch.where(ev['tau']==t)[0]
            for ii in ids.tolist():
                jj=int(ev['j'][ii]); vv=ev['val'][ii]
                if int(ev['typ'][ii])==0: x[ii,:,jj]=x[ii,:,jj]+vv
                elif int(ev['typ'][ii])==1: x[ii,:,jj]=vv
                else: bc[ii,:,jj]=bc[ii,:,jj]+vv
        x=torch.einsum('bkij,bkj->bki',M,x)+bc
        done=(h==(t+1))
        if done.any(): out[done]=x[done]
    return out

def tensor(a,dtype=None):
    return torch.tensor(np.asarray(a),dtype=dtype) if dtype else torch.tensor(np.asarray(a))

def sample_train(rng,ids,Ms,bs,eqbank,tmbank,B=80):
    wi=rng.choice(ids,B,replace=True); C=[];KI=[];x0=[];hs=[];ty=[];js=[];vals=[];taus=[];ye=[];yp=[];us=[];yeq=[]
    for w in wi:
        c,k=make_context(rng,w,eqbank,tmbank); C.append(c);KI.append(k)
        h=int(rng.integers(4,9)); off=int(rng.integers(1,min(5,h))); tau=h-off
        typ=int(rng.integers(0,3)); j=int(rng.integers(D)); val=float(rng.uniform(-1.6,1.6)); x=rng.uniform(-1.3,1.3,D).astype('float32')
        x0.append(x); hs.append(h); ty.append(typ); js.append(j); vals.append(val); taus.append(tau)
        ye.append(rollout_event_np(Ms[w],bs[w],x,h,typ,j,val,tau)); yp.append(cg.rollout_np(Ms[w],bs[w],x,h))
        u=rng.uniform(-1.2,1.2,D).astype('float32'); us.append(u); yeq.append(cg.equilibrium(Ms[w],bs[w],u))
    return dict(wi=wi,C=tensor(C),KI=tensor(KI,torch.long),x0=tensor(x0),h=tensor(hs,torch.long),typ=tensor(ty,torch.long),j=tensor(js,torch.long),val=tensor(vals),tau=tensor(taus,torch.long),ye=tensor(ye),yp=tensor(yp),u=tensor(us),yeq=tensor(yeq))

def loss_batch(model,batch,steps):
    M,b,lg=model.form_world(batch['C'],batch['KI'],steps=steps)
    pe=cg.expected(exec_event_torch(M,b,batch['x0'],batch['h'],batch['typ'],batch['j'],batch['val'],batch['tau']),lg)
    pp=cg.expected(cg.exec_temp(M,b,batch['x0'],batch['h']),lg)
    pq=cg.expected(cg.exec_eq(M,b,batch['u']),lg)
    le=((pe-batch['ye'])**2).mean(); lp=((pp-batch['yp'])**2).mean(); lq=((pq-batch['yeq'])**2).mean()
    return le + .30*lp + .20*lq, le, lp, lq

def train(seed,Ms,bs,eqbank,tmbank,train_ids,dev_ids,updates=500):
    ck=torch.load(ROOT/'models'/f'cg023_{seed}.pt',map_location='cpu',weights_only=False)
    model=cg.WorldProgram(); model.load_state_dict(ck['world']); model.train(); opt=torch.optim.Adam(model.parameters(),lr=7.5e-4)
    rng=np.random.default_rng(24000+seed); best=1e9; bestsd=None; beststep=None; logs=[]
    for step in range(1,updates+1):
        bt=sample_train(rng,train_ids,Ms,bs,eqbank,tmbank,B=80)
        opt.zero_grad(); loss,le,lp,lq=loss_batch(model,bt,int(rng.integers(3,7))); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),5); opt.step()
        if step%50==0:
            model.eval(); dv=sample_train(np.random.default_rng(80000+seed+step),dev_ids,Ms,bs,eqbank,tmbank,B=240)
            with torch.no_grad(): vl,vle,vlp,vlq=loss_batch(model,dv,4)
            rec={'step':step,'train_total':float(loss.detach()),'train_event':float(le.detach()),'dev_total':float(vl),'dev_event':float(vle),'dev_passive':float(vlp),'dev_eq':float(vlq)};logs.append(rec)
            if float(vl)<best: best=float(vl); bestsd=copy.deepcopy(model.state_dict()); beststep=step
            print(seed,step,float(vl),float(vle),float(vlp),float(vlq),flush=True); model.train()
    model.load_state_dict(bestsd); model.eval(); torch.save({'world':bestsd,'seed':seed,'selected_step':beststep},OUT/'models'/f'cg024_{seed}.pt'); (OUT/'models'/f'cg024_{seed}_training.json').write_text(json.dumps(logs,indent=2))
    return model,{'seed':seed,'selected_step':beststep,'dev_total':best}

def eval_panel(model,seed,Ms,bs,eqbank,tmbank,test_ids):
    rng=np.random.default_rng(24100); rows=[]
    horizons=[8,16,32,64,128]
    with torch.no_grad():
        for w in test_ids:
            c,k=make_context(rng,w,eqbank,tmbank); C=tensor(c[None]);KI=tensor(k[None],torch.long); M,b,lg=model.form_world(C,KI,steps=4)
            for typ,name in [(0,'impulse'),(1,'clamp'),(2,'persistent_force')]:
                for h in horizons:
                    off=2 if h>=4 else 1; tau=h-off; j=int(rng.integers(D)); val=float(rng.uniform(-1.5,1.5)); x0=rng.uniform(-1.3,1.3,D).astype('float32')
                    truth=rollout_event_np(Ms[w],bs[w],x0,h,typ,j,val,tau)
                    H=tensor([h],torch.long);T=tensor([typ],torch.long);J=tensor([j],torch.long);V=tensor([val]);TA=tensor([tau],torch.long);X=tensor(x0[None])
                    pc=cg.expected(exec_event_torch(M,b,X,H,T,J,V,TA),lg)[0].numpy(); pi=cg.expected(cg.exec_temp(M,b,X,H),lg)[0].numpy()
                    wrongj=(j+1)%D; pwj=cg.expected(exec_event_torch(M,b,X,H,T,tensor([wrongj],torch.long),V,TA),lg)[0].numpy()
                    wt=max(0,tau-2); pwt=cg.expected(exec_event_torch(M,b,X,H,T,J,V,tensor([wt],torch.long)),lg)[0].numpy()
                    for cond,p in [('correct',pc),('ignore',pi),('wrong_target',pwj),('wrong_time',pwt)]:
                        rows.append({'seed':seed,'world_id':int(w),'operation':name,'horizon':h,'condition':cond,'mse':float(((p-truth)**2).mean())})
            # unseen composition: persistent force then later impulse
            for h in [16,32,64,128]:
                tau1=h-4; tau2=h-2; j1=int(rng.integers(D));j2=int(rng.integers(D));v1=float(rng.uniform(-1.2,1.2));v2=float(rng.uniform(-1.2,1.2));x0=rng.uniform(-1.3,1.3,D).astype('float32')
                evs=[(2,j1,v1,tau1),(0,j2,v2,tau2)];truth=rollout_events_np(Ms[w],bs[w],x0,h,evs)
                H=tensor([h],torch.long);X=tensor(x0[None])
                ev1={'typ':tensor([2],torch.long),'j':tensor([j1],torch.long),'val':tensor([v1]),'tau':tensor([tau1],torch.long)}
                ev2={'typ':tensor([0],torch.long),'j':tensor([j2],torch.long),'val':tensor([v2]),'tau':tensor([tau2],torch.long)}
                pc=cg.expected(exec_two_events_torch(M,b,X,H,ev1,ev2),lg)[0].numpy(); omit=cg.expected(exec_event_torch(M,b,X,H,ev1['typ'],ev1['j'],ev1['val'],ev1['tau']),lg)[0].numpy()
                for cond,p in [('correct',pc),('omit_second',omit)]: rows.append({'seed':seed,'world_id':int(w),'operation':'compound_force_plus_impulse','horizon':h,'condition':cond,'mse':float(((p-truth)**2).mean())})
    return pd.DataFrame(rows)

def passive_panel(model,seed,Ms,bs,eqbank,tmbank,test_ids):
    rng=np.random.default_rng(24200); rows=[]
    with torch.no_grad():
        for w in test_ids:
            c,k=make_context(rng,w,eqbank,tmbank); M,b,lg=model.form_world(tensor(c[None]),tensor(k[None],torch.long),steps=4)
            for h in [32,64,128]:
                x0=rng.uniform(-1.3,1.3,D).astype('float32');truth=cg.rollout_np(Ms[w],bs[w],x0,h);pred=cg.expected(cg.exec_temp(M,b,tensor(x0[None]),tensor([h],torch.long)),lg)[0].numpy();rows.append({'seed':seed,'world_id':int(w),'horizon':h,'mse':float(((pred-truth)**2).mean())})
    return pd.DataFrame(rows)

def bootstrap_diff(df,a,b,group_cols=['world_id'],n=5000,seed=24):
    # pair conditions within seed/world/operation/horizon, aggregate seeds then bootstrap worlds
    key=['seed','world_id','operation','horizon']; p=df[df.condition.isin([a,b])].pivot_table(index=key,columns='condition',values='mse').dropna(); p['diff']=p[a]-p[b]
    wg=p.reset_index().groupby('world_id').diff.mean(); vals=wg.to_numpy(); rng=np.random.default_rng(seed); boot=np.mean(rng.choice(vals,(n,len(vals)),replace=True),axis=1)
    return float(vals.mean()),float(np.quantile(boot,.025)),float(np.quantile(boot,.975)),float((vals<0).mean())

def main():
    torch.set_num_threads(4); dat=np.load(ROOT/'world_data.npz');Ms,bs,eqbank,tmbank=dat['M'],dat['b'],dat['eqbank'],dat['tmbank']; train_ids=np.arange(400);dev_ids=np.arange(400,500);test_ids=np.arange(500,600)
    mets=[];allrows=[];passrows=[]
    for seed in SEEDS:
        model,m=train(seed,Ms,bs,eqbank,tmbank,train_ids,dev_ids);mets.append(m);allrows.append(eval_panel(model,seed,Ms,bs,eqbank,tmbank,test_ids));passrows.append(passive_panel(model,seed,Ms,bs,eqbank,tmbank,test_ids))
    pd.DataFrame(mets).to_csv(OUT/'training_summary.csv',index=False);df=pd.concat(allrows,ignore_index=True);df.to_csv(OUT/'sequential_eval_detail.csv',index=False);pdf=pd.concat(passrows,ignore_index=True);pdf.to_csv(OUT/'passive_long_horizon.csv',index=False)
    summaries=[]
    for op in df.operation.unique():
        sub=df[df.operation==op]
        base='omit_second' if op.startswith('compound') else 'ignore'
        d,lo,hi,rate=bootstrap_diff(sub,'correct',base); summaries.append({'operation':op,'comparison':f'correct_minus_{base}','mean_diff':d,'ci95_low':lo,'ci95_high':hi,'correct_lower_world_fraction':rate})
        if not op.startswith('compound'):
            for ctrl in ['wrong_target','wrong_time']:
                d,lo,hi,rate=bootstrap_diff(sub,'correct',ctrl); summaries.append({'operation':op,'comparison':f'correct_minus_{ctrl}','mean_diff':d,'ci95_low':lo,'ci95_high':hi,'correct_lower_world_fraction':rate})
    pd.DataFrame(summaries).to_csv(OUT/'acceptance_summary.csv',index=False)
    # horizon aggregate correct vs ignore
    agg=df.groupby(['operation','horizon','condition'],as_index=False).mse.mean();agg.to_csv(OUT/'horizon_summary.csv',index=False)
    # state replay verification from trained ckpts
    ver=[]
    for seed in SEEDS:
        ck=torch.load(OUT/'models'/f'cg024_{seed}.pt',map_location='cpu',weights_only=False);model=cg.WorldProgram();model.load_state_dict(ck['world']);model.eval();rng=np.random.default_rng(24300);Cs=[];Ks=[]
        for w in test_ids[:32]:c,k=make_context(rng,w,eqbank,tmbank);Cs.append(c);Ks.append(k)
        C=tensor(Cs);KI=tensor(Ks,torch.long)
        with torch.no_grad():
            M2,b2,l2=model.form_world(C,KI,steps=2);Mr,br,lr=model.form_world(C,KI,steps=2,start_state=(M2,b2,l2));M4,b4,l4=model.form_world(C,KI,steps=4)
            err=max(float((Mr-M4).abs().max()),float((br-b4).abs().max()),float((lr-l4).abs().max()));rowsum=float(M4.abs().sum(-1).max())
        ver.append({'seed':seed,'state_replay_max_abs':err,'max_row_abs_sum':rowsum})
    (OUT/'verification.json').write_text(json.dumps(ver,indent=2)); print(pd.DataFrame(mets)); print(pd.DataFrame(summaries)); print('COMPLETE')
if __name__=='__main__': main()
