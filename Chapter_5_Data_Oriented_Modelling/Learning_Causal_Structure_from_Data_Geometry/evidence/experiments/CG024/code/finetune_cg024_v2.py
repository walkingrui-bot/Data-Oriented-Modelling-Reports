from pathlib import Path
import sys,copy,json
import numpy as np,pandas as pd,torch
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT))
import run_cg023_coordinate_world as cg
import run_cg024_sequential_acceptance as r
OUT=Path('/mnt/data/cg024_final/CAUSAL_GEOMETRY_024'); D,K=cg.D,cg.K

def evidence_fit(M,b,lg,C,KI):
    w=lg.softmax(-1); losses=[]
    # tokenwise temporal/equilibrium consistency, mixture expected
    for t in range(C.shape[1]):
        x=C[:,t,:D]; y=C[:,t,D:]; kt=KI[:,t]
        pred=torch.zeros_like(y)
        mt=(kt==1)
        if mt.any():
            pc=torch.einsum('bkij,bj->bki',M[mt],x[mt])+b[mt]
            pred[mt]=(pc*w[mt,:,None]).sum(1)
        me=(kt==0)
        if me.any():
            pc=cg.exec_eq(M[me],b[me],x[me])
            pred[me]=(pc*w[me,:,None]).sum(1)
        losses.append(((pred-y)**2).mean())
    return torch.stack(losses).mean()

def full_loss(model,bt,steps):
    M,b,lg=model.form_world(bt['C'],bt['KI'],steps=steps)
    pe=cg.expected(r.exec_event_torch(M,b,bt['x0'],bt['h'],bt['typ'],bt['j'],bt['val'],bt['tau']),lg)
    pp=cg.expected(cg.exec_temp(M,b,bt['x0'],bt['h']),lg)
    pq=cg.expected(cg.exec_eq(M,b,bt['u']),lg)
    le=((pe-bt['ye'])**2).mean(); lp=((pp-bt['yp'])**2).mean(); lq=((pq-bt['yeq'])**2).mean()
    ld=(((pe-pp)-(bt['ye']-bt['yp']))**2).mean(); lf=evidence_fit(M,b,lg,bt['C'],bt['KI'])
    total=le+.35*lp+.20*lq+2.0*ld+0.75*lf
    return total,le,lp,lq,ld,lf

def train_v2(seed,Ms,bs,eqbank,tmbank,train_ids,dev_ids,updates=450):
    ck=torch.load(OUT/'models'/f'cg024_{seed}.pt',map_location='cpu',weights_only=False); model=cg.WorldProgram();model.load_state_dict(ck['world']);model.train();opt=torch.optim.Adam(model.parameters(),lr=5e-4);rng=np.random.default_rng(24500+seed)
    best=1e9;bestsd=None;bstep=None;logs=[]
    for step in range(1,updates+1):
        bt=r.sample_train(rng,train_ids,Ms,bs,eqbank,tmbank,B=80);opt.zero_grad();vals=full_loss(model,bt,int(rng.integers(3,7)));vals[0].backward();torch.nn.utils.clip_grad_norm_(model.parameters(),5);opt.step()
        if step%50==0:
            model.eval();dv=r.sample_train(np.random.default_rng(90000+seed+step),dev_ids,Ms,bs,eqbank,tmbank,B=240)
            with torch.no_grad(): vv=full_loss(model,dv,4)
            names=['total','event','passive','eq','delta','evidence_fit'];rec={'step':step,**{f'dev_{n}':float(v) for n,v in zip(names,vv)}};logs.append(rec)
            if float(vv[0])<best:best=float(vv[0]);bestsd=copy.deepcopy(model.state_dict());bstep=step
            print('V2',seed,step,*[round(float(x),6) for x in vv],flush=True);model.train()
    model.load_state_dict(bestsd);model.eval();torch.save({'world':bestsd,'seed':seed,'selected_step':bstep},OUT/'models'/f'cg024_{seed}_final.pt');(OUT/'models'/f'cg024_{seed}_final_training.json').write_text(json.dumps(logs,indent=2));return model,{'seed':seed,'selected_step':bstep,'dev_total':best}

def summarize(df):
    rec=[]
    for op in df.operation.unique():
        sub=df[df.operation==op];base='omit_second' if op.startswith('compound') else 'ignore'
        for ctrl in [base]+([] if op.startswith('compound') else ['wrong_target','wrong_time']):
            d,lo,hi,rate=boot(sub,'correct',ctrl);rec.append({'operation':op,'comparison':f'correct_minus_{ctrl}','mean_diff':d,'ci95_low':lo,'ci95_high':hi,'correct_lower_world_fraction':rate})
    return pd.DataFrame(rec)
def boot(sub,a,b,n=5000,seed=25):
    p=sub[sub.condition.isin([a,b])].pivot_table(index=['seed','world_id','operation','horizon'],columns='condition',values='mse').dropna();p['delta']=p[a]-p[b];vals=p.reset_index().groupby('world_id')['delta'].mean().to_numpy();rng=np.random.default_rng(seed);bt=np.mean(rng.choice(vals,(n,len(vals)),replace=True),axis=1);return float(vals.mean()),float(np.quantile(bt,.025)),float(np.quantile(bt,.975)),float((vals<0).mean())
def main():
    torch.set_num_threads(4);dat=np.load(ROOT/'world_data.npz');Ms,bs,eqbank,tmbank=dat['M'],dat['b'],dat['eqbank'],dat['tmbank'];tr=np.arange(400);dv=np.arange(400,500);te=np.arange(500,600);mets=[];rows=[];passr=[]
    for seed in [11,22]:
        model,m=train_v2(seed,Ms,bs,eqbank,tmbank,tr,dv);mets.append(m);rows.append(r.eval_panel(model,seed,Ms,bs,eqbank,tmbank,te));passr.append(r.passive_panel(model,seed,Ms,bs,eqbank,tmbank,te))
    df=pd.concat(rows,ignore_index=True);pd.DataFrame(mets).to_csv(OUT/'final_training_summary.csv',index=False);df.to_csv(OUT/'sequential_eval_detail_final.csv',index=False);pd.concat(passr).to_csv(OUT/'passive_long_horizon_final.csv',index=False);summ=summarize(df);summ.to_csv(OUT/'acceptance_summary_final.csv',index=False);df.groupby(['operation','horizon','condition'],as_index=False).mse.mean().to_csv(OUT/'horizon_summary_final.csv',index=False);print(summ.to_string(index=False));print('FINAL_COMPLETE')
if __name__=='__main__':main()
