from pathlib import Path
import json, math, shutil
import numpy as np
import pandas as pd
import torch
from scipy.special import logsumexp
import run_cg018 as cg18

ROOT=Path(__file__).resolve().parent
OUT=ROOT
(OUT/'figures').mkdir(parents=True,exist_ok=True)
SIGMA=0.15
SEEDS=[11,22,33]
MODES=['mechanism_blank','mechanism_feedback']

def solve_clamp(B, targets, values):
    B=np.asarray(B); n=B.shape[-1]
    C=B.copy(); rhs=np.zeros(B.shape[:-2]+(n,),dtype=float)
    for t,v in zip(targets,values): C[...,t,:]=0.0; rhs[...,t]=v
    A=np.eye(n)-C
    return np.linalg.solve(A,rhs[...,None])[...,0]

def per_query_nll(mus,w,y):
    logw=np.log(np.clip(w,1e-12,1.0))
    ld=-.5*np.square((mus-y[:,None,:])/SIGMA).sum(-1)-mus.shape[-1]*math.log(SIGMA*math.sqrt(2*math.pi))
    return -logsumexp(logw+ld,axis=1)

def metric_arrays(mus,w,y):
    nll=per_query_nll(mus,w,y)
    mean=(mus*w[:,:,None]).sum(1)
    mse=np.square(mean-y).mean(-1)
    dist=np.sqrt(np.square(mus-y[:,None,:]).mean(-1))
    cov=np.any((dist<=.20)&(w>=.10),axis=1).astype(float)
    return nll,mse,cov,mean

def summarize(arr): return float(np.mean(arr))

def bootstrap_group(diff_by_group, seed=19019, B=10000):
    # diff positive means first method is better (control metric - mechanism metric)
    v=np.asarray(diff_by_group,float); rng=np.random.default_rng(seed)
    means=np.empty(B)
    for b in range(B): means[b]=rng.choice(v,size=len(v),replace=True).mean()
    return float(v.mean()), float(np.quantile(means,.025)), float(np.quantile(means,.975)), float(np.mean(v>0))

def main():
    torch.set_num_threads(1)
    z=np.load(ROOT/'synthetic_data.npz'); ii=np.flatnonzero(z['split']==2)
    x=torch.tensor(z['x'][ii],dtype=torch.float32); trueB=z['true_B'][ii]
    support=z['support'][ii]; groups=z['group'][ii]
    summary=[]; dq=[]; eq=[]; group_rows=[]
    pair_list=[(0,1),(0,2),(1,2)]; value_list=[(1.,1.),(1.,-1.),(-1.,1.),(-1.,-1.)]
    offdiag=[(r,s) for r in range(3) for s in range(3) if r!=s]

    for mode in MODES:
      for seed in SEEDS:
        ck=torch.load(ROOT/'models'/f'synthetic_worlds_{mode}_{seed}.pt',weights_only=True)
        model=cg18.MechanismModel('synthetic',mode); model.load_state_dict(ck['state_dict']); model.eval()
        with torch.no_grad(): _,tr=model(x,trace=True)
        B=tr['B'][:,-1].numpy(); w=tr['weights'][:,-1].numpy(); sims=tr['simulations'][:,-1].numpy()

        # Novel double-do queries.
        for p in pair_list:
          for vals in value_list:
            y=solve_clamp(trueB,p,vals); mech=solve_clamp(B,p,vals)
            sup=vals[0]*sims[:,:,p[0],:]+vals[1]*sims[:,:,p[1],:]
            sup[:,:,p[0]]=vals[0]; sup[:,:,p[1]]=vals[1]
            for method,mus in [('mechanism_solve',mech),('single_do_superposition',sup)]:
                nll,mse,cov,_=metric_arrays(mus,w,y)
                for n in range(len(x)):
                    dq.append({'mode':mode,'seed':seed,'group':int(groups[n]),'support':int(support[n]),'targets':f'{p[0]}+{p[1]}','values':f'{vals[0]:+.0f},{vals[1]:+.0f}','method':method,'nll':float(nll[n]),'mse':float(mse[n]),'coverage':float(cov[n])})

        # Unseen true-edge deletion and wrong-coordinate controls.
        for n in range(len(x)):
            edges=[tuple(e) for e in np.argwhere(np.abs(trueB[n])>1e-9)]
            assert len(edges)==2
            absent=[e for e in offdiag if e not in edges]
            for edge_idx,(r,s) in enumerate(edges):
                bt=trueB[n].copy(); bt[r,s]=0.0
                yt=solve_clamp(bt[None],[s],[1.0])[0]; y0=solve_clamp(trueB[n:n+1],[s],[1.0])[0]
                # correct semantic edit
                bc=B[n].copy(); bc[:,r,s]=0.0; pe=solve_clamp(bc,[s],[1.0])
                # no edit
                pi=sims[n,:,s,:]
                # all four absent-coordinate deletions, retained separately
                preds={'apply_true_edge_delete':pe,'ignore_edge_delete':pi}
                for j,(wr,ws) in enumerate(absent):
                    bw=B[n].copy(); bw[:,wr,ws]=0.0
                    preds[f'wrong_edge_{j}']=solve_clamp(bw,[s],[1.0])
                m0=(pi*w[n,:,None]).sum(0); me=(pe*w[n,:,None]).sum(0)
                for method,mus1 in preds.items():
                    nll,mse,cov,mean=metric_arrays(mus1[None],w[n:n+1],yt[None])
                    eq.append({'mode':mode,'seed':seed,'group':int(groups[n]),'case':int(n),'support':int(support[n]),'edge_index':edge_idx,'response':int(r),'source':int(s),'true_edge':float(trueB[n,r,s]),'method':method,'nll':float(nll[0]),'mse':float(mse[0]),'coverage':float(cov[0]),'true_delta_response':float(yt[r]-y0[r]),'pred_delta_response':float(me[r]-m0[r]) if method=='apply_true_edge_delete' else np.nan})

        

    dq=pd.DataFrame(dq); eq=pd.DataFrame(eq)
    dq.to_csv(OUT/'double_do_query_level.csv',index=False); eq.to_csv(OUT/'edge_delete_query_level.csv',index=False)

    # Aggregate wrong-edge controls into one comparison distribution.
    eq2=eq.copy(); eq2['method_group']=eq2.method.where(~eq2.method.str.startswith('wrong_edge_'),'wrong_edge_delete')
    for df,test,mg in [(dq,'double_do','method'),(eq2,'edge_delete','method_group')]:
      for (mode,seed,method,subset),g in df.assign(subset=np.where(df.support.eq(1),'support','no_support')).groupby(['mode','seed',mg,'subset']):
        summary.append({'test':test,'mode':mode,'seed':seed,'method':method,'subset':subset,'n_queries':len(g),'nll':g.nll.mean(),'mse':g.mse.mean(),'coverage':g.coverage.mean()})
      for (mode,seed,method),g in df.groupby(['mode','seed',mg]):
        summary.append({'test':test,'mode':mode,'seed':seed,'method':method,'subset':'all','n_queries':len(g),'nll':g.nll.mean(),'mse':g.mse.mean(),'coverage':g.coverage.mean()})

    # Edge semantic delta diagnostic only on correct edits.
    sem=eq[eq.method.eq('apply_true_edge_delete')].copy()
    sem_summary=[]
    for (mode,seed),g in sem.groupby(['mode','seed']):
        corr=np.corrcoef(g.true_delta_response,g.pred_delta_response)[0,1]
        sign=np.mean(np.sign(g.true_delta_response)==np.sign(g.pred_delta_response))
        sem_summary.append({'mode':mode,'seed':seed,'n':len(g),'delta_corr':corr,'delta_sign_accuracy':sign,'delta_mse':np.mean((g.true_delta_response-g.pred_delta_response)**2)})
    pd.DataFrame(sem_summary).to_csv(OUT/'edge_semantic_summary.csv',index=False)

    # Group-level paired controls, averaged across three seeds before bootstrap.
    # Double-do: superposition - mechanism (positive means mechanism solve better).
    dg=dq.groupby(['mode','seed','group','method'])[['nll','mse']].mean().unstack('method')
    eg=eq2.groupby(['mode','seed','group','method_group'])[['nll','mse']].mean().unstack('method_group')
    infer=[]
    for mode in MODES:
        d=dg.loc[mode]
        diff_nll=(d['nll']['single_do_superposition']-d['nll']['mechanism_solve']).groupby('group').mean()
        diff_mse=(d['mse']['single_do_superposition']-d['mse']['mechanism_solve']).groupby('group').mean()
        for metric,v in [('nll_improvement',diff_nll),('mse_improvement',diff_mse)]:
            mean,lo,hi,share=bootstrap_group(v,19019+(0 if mode=='mechanism_blank' else 100)+(0 if metric.startswith('nll') else 1))
            infer.append({'test':'double_do','mode':mode,'contrast':'superposition_minus_mechanism','metric':metric,'mean':mean,'bootstrap_95_lo':lo,'bootstrap_95_hi':hi,'group_fraction_positive':share,'n_groups':len(v)})
        e=eg.loc[mode]
        for ctrl in ['ignore_edge_delete','wrong_edge_delete']:
            diff_nll=(e['nll'][ctrl]-e['nll']['apply_true_edge_delete']).groupby('group').mean()
            diff_mse=(e['mse'][ctrl]-e['mse']['apply_true_edge_delete']).groupby('group').mean()
            for metric,v in [('nll_improvement',diff_nll),('mse_improvement',diff_mse)]:
                mean,lo,hi,share=bootstrap_group(v,20019+(0 if mode=='mechanism_blank' else 100)+(10 if ctrl.startswith('wrong') else 0)+(0 if metric.startswith('nll') else 1))
                infer.append({'test':'edge_delete','mode':mode,'contrast':ctrl+'_minus_true_edit','metric':metric,'mean':mean,'bootstrap_95_lo':lo,'bootstrap_95_hi':hi,'group_fraction_positive':share,'n_groups':len(v)})
    pd.DataFrame(infer).to_csv(OUT/'group_level_controls.csv',index=False)
    pd.DataFrame(summary).to_csv(OUT/'summary.csv',index=False)
    np.savez_compressed(OUT/'synthetic_test_context.npz',x=z['x'][ii],true_B=trueB,support=support,group=groups,query=z['query'][ii])
    print('\nSUMMARY\n',pd.DataFrame(summary).to_string(index=False))
    print('\nGROUP CONTROLS\n',pd.DataFrame(infer).to_string(index=False))
    print('\nEDGE SEMANTICS\n',pd.DataFrame(sem_summary).to_string(index=False))

if __name__=='__main__': main()
