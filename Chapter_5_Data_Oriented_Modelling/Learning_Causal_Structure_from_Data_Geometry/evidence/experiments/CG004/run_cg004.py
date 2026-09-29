import numpy as np, pandas as pd, math
from scipy.stats import norm
import matplotlib.pyplot as plt

OUT='/mnt/data/causal_geometry_004'
RHO=0.65
POOL_HALF=160000
REPS=160
THETAS=np.array([0.03,0.06,0.10,0.15])
NS=np.array([100,400,1600])
SEED=20260927
rng=np.random.default_rng(SEED)

# ---------- exact swap-paired Gaussian baseline ----------
x0=rng.normal(size=POOL_HALF)
e0=rng.normal(size=POOL_HALF)
y0=RHO*x0+np.sqrt(1-RHO**2)*e0
x=np.concatenate([x0,y0])
y=np.concatenate([y0,x0])
N=len(x)


def raw_modes(x,y):
    s=np.sqrt(1-RHO**2)
    ef=(y-RHO*x)/s
    er=(x-RHO*y)/s
    return np.column_stack([
        # H: conditional-width / heteroscedastic-like asymmetry
        np.tanh(x)*np.tanh(ef**2-1.0) - np.tanh(y)*np.tanh(er**2-1.0),
        # M: nonlinear conditional-mean-like asymmetry
        np.tanh(x**2-1.0)*np.tanh(ef) - np.tanh(y**2-1.0)*np.tanh(er),
        # S: residual skew/shape asymmetry
        np.tanh(ef)**3 - np.tanh(er)**3,
        # T: residual tail-width asymmetry
        np.tanh(np.abs(ef)-0.8) - np.tanh(np.abs(er)-0.8),
    ])

R=raw_modes(x,y)
# Ordered Gram-Schmidt under the baseline Fisher inner product.
Q=np.zeros_like(R)
coef=[]
for j in range(R.shape[1]):
    v=R[:,j].copy()
    c=[]
    for k in range(j):
        ck=np.mean(v*Q[:,k])
        v-=ck*Q[:,k]
        c.append(ck)
    scale=np.sqrt(np.mean(v*v))
    Q[:,j]=v/scale
    coef.append((c,scale))

# Swap-symmetric tangent nuisance scores: all satisfy s(x,y)=s(y,x)
S=np.column_stack([
    np.tanh((x+y)/2.0),
    np.tanh(x*y),
    np.tanh(x*x+y*y-2.0),
])

nuisances={
    'none':np.array([0.0,0.0,0.0]),
    'common_mean':np.array([0.8,0.0,0.0]),
    'correlation':np.array([0.0,0.8,0.0]),
    'radial_scale':np.array([0.0,0.0,0.8]),
    'combined':np.array([0.5,-0.5,0.5]),
}

# Pure and mixed normal directions (unit Euclidean norm in base-whitened Q coordinates)
dirs={
    'H':np.array([1,0,0,0.],float),
    'M':np.array([0,1,0,0.],float),
    'S':np.array([0,0,1,0.],float),
    'T':np.array([0,0,0,1.],float),
    'HM':np.array([1,1,0,0.],float)/np.sqrt(2),
    'MS':np.array([0,1,1,0.],float)/np.sqrt(2),
    'HMS':np.array([1,-1,1,0.],float)/np.sqrt(3),
    'ALL':np.ones(4)/2,
}

# Baseline checks
base_cov=(Q.T@Q)/N
swap_err=np.max(np.abs(Q[:POOL_HALF]+Q[POOL_HALF:]))

# ---------- tangent-dependent normal Fisher tensors ----------
fisher_rows=[]
fisher_mats={}
eta_weights={}
for name,eta in nuisances.items():
    lw=S@eta
    lw-=lw.max()
    w=np.exp(lw); w/=w.sum()
    eta_weights[name]=w
    mu=(w[:,None]*Q).sum(0)
    Z=Q-mu
    G=(Z.T*w)@Z
    fisher_mats[name]=G
    eig=np.linalg.eigvalsh(G)
    fisher_rows.append({
        'nuisance':name,
        'eig_min':eig.min(),'eig_max':eig.max(),'condition_number':eig.max()/eig.min(),
        'max_abs_offdiag':np.max(np.abs(G-np.diag(np.diag(G)))),
        **{f'G{i+1}{j+1}':G[i,j] for i in range(4) for j in range(4)}
    })
fisher_df=pd.DataFrame(fisher_rows)
fisher_df.to_csv(f'{OUT}/cg004_fisher_tensors.csv',index=False)

# Utility: sample from discrete weighted pool via CDF
def weighted_sample_sums(values, w, ns, reps, rng):
    cdf=np.cumsum(w); cdf[-1]=1.0
    out={}
    for n in ns:
        u=rng.random(reps*int(n))
        idx=np.searchsorted(cdf,u,side='right')
        vals=values[idx].reshape(reps,int(n))
        out[int(n)]=vals.sum(axis=1)
    return out

# ---------- main grid ----------
rows=[]
for nname,eta in nuisances.items():
    w_eta=eta_weights[nname]
    G=fisher_mats[nname]
    for dname,u in dirs.items():
        psi=Q@u
        I_eta=float(u@G@u)
        for theta in THETAS:
            # p+ proportional p_eta * exp(theta psi)
            lw=np.log(w_eta+1e-300)+theta*psi
            lw-=lw.max()
            wp=np.exp(lw); wp/=wp.sum()
            # exact KL to the swap-symmetric fixed-point set: projection is (P+ + P-)/2
            # because p-/p+=exp(-2 theta psi) and normalizers match by paired symmetry.
            log_ratio=np.log(2.0)-np.logaddexp(0.0,-2*theta*psi)
            D_R=float(np.sum(wp*log_ratio))
            mu=float(np.sum(wp*psi))
            var=float(np.sum(wp*(psi-mu)**2))
            # One CDF per distribution; draw sums for all n.
            sums=weighted_sample_sums(psi,wp,NS,REPS,rng)
            for n in NS:
                ss=sums[int(n)]
                acc=float(np.mean(ss>0))
                snr=float(np.sqrt(n)*mu/np.sqrt(var))
                z_raw=float(theta*np.sqrt(n))
                z_fisher=float(theta*np.sqrt(n*I_eta))
                z_D=float(np.sqrt(2*n*D_R))
                rows.append({
                    'nuisance':nname,'direction':dname,'theta':float(theta),'n':int(n),
                    'I_eta':I_eta,'D_R':D_R,'nD_R':n*D_R,
                    'mu_psi':mu,'var_psi':var,'snr_exact_moment':snr,
                    'accuracy_empirical':acc,
                    'z_raw':z_raw,'z_fisher':z_fisher,'z_D':z_D,
                    'pred_raw':norm.cdf(z_raw),'pred_fisher':norm.cdf(z_fisher),'pred_D':norm.cdf(z_D),
                })
main=pd.DataFrame(rows)
main.to_csv(f'{OUT}/cg004_main_grid.csv',index=False)

# Prediction summaries: local regime and full grid
summ=[]
for label,df in [('all',main),('local_theta_le_0.10',main[main.theta<=.10])]:
    for pred in ['pred_raw','pred_fisher','pred_D']:
        y=df.accuracy_empirical.values; p=df[pred].values
        summ.append({
            'scope':label,'predictor':pred,
            'MAE':np.mean(np.abs(y-p)),
            'RMSE':np.sqrt(np.mean((y-p)**2)),
            'corr':np.corrcoef(y,p)[0,1]
        })
pred_summary=pd.DataFrame(summ)
pred_summary.to_csv(f'{OUT}/cg004_prediction_summary.csv',index=False)

# SNR relation to z_D
sub=main[main.theta<=.10]
k=(sub.z_D*sub.snr_exact_moment).sum()/(sub.z_D**2).sum()
pred_snr=k*sub.z_D
r2=1-((sub.snr_exact_moment-pred_snr)**2).sum()/((sub.snr_exact_moment-sub.snr_exact_moment.mean())**2).sum()

# ---------- wrong-expert transfer matrix ----------
# Pure directions only, no nuisance, theta=.08, n=800
pure=['H','M','S','T']; theta=.08; n=800; reps=800
w_eta=eta_weights['none']
transfer=np.zeros((4,4))
for i,dname in enumerate(pure):
    u=dirs[dname]; psi=Q@u
    lw=np.log(w_eta+1e-300)+theta*psi; lw-=lw.max(); wp=np.exp(lw); wp/=wp.sum()
    cdf=np.cumsum(wp); cdf[-1]=1
    U=rng.random(reps*n)
    idx=np.searchsorted(cdf,U,side='right').reshape(reps,n)
    # each expert k uses sum Q_k
    for k in range(4):
        s=Q[idx,k].sum(axis=1)
        transfer[i,k]=np.mean(s>0)
transfer_df=pd.DataFrame(transfer,index=pure,columns=pure)
transfer_df.to_csv(f'{OUT}/cg004_expert_transfer.csv')

# ---------- tangent-only controls ----------
tan_rows=[]; n=800; reps=1000
for nname,w in eta_weights.items():
    cdf=np.cumsum(w); cdf[-1]=1
    idx=np.searchsorted(cdf,rng.random(reps*n),side='right').reshape(reps,n)
    for k,dname in enumerate(pure):
        acc=np.mean(Q[idx,k].sum(axis=1)>0)
        tan_rows.append({'nuisance':nname,'score':dname,'accuracy':acc})
tan_df=pd.DataFrame(tan_rows)
tan_df.to_csv(f'{OUT}/cg004_tangent_controls.csv',index=False)

# ---------- figures ----------
# Fig 10: Fisher tensors
fig,axs=plt.subplots(1,5,figsize=(13.5,3.0),sharex=True,sharey=True)
vmin=.0; vmax=1.8
for ax,(name,G) in zip(axs,fisher_mats.items()):
    im=ax.imshow(G,vmin=vmin,vmax=vmax,cmap='viridis')
    ax.set_title(name.replace('_',' '),fontsize=9)
    ax.set_xticks(range(4),pure); ax.set_yticks(range(4),pure)
    for i in range(4):
        for j in range(4):
            ax.text(j,i,f'{G[i,j]:.2f}',ha='center',va='center',fontsize=6,
                    color='white' if G[i,j]>.9 else 'black')
fig.colorbar(im,ax=axs.ravel().tolist(),shrink=.75,label='Local Fisher metric')
fig.suptitle('Tangent nuisance reshapes the metric on the normal subspace',y=1.02,fontsize=12)
fig.subplots_adjust(wspace=.28,right=.92,top=.82,bottom=.15)
fig.savefig(f'{OUT}/fig10_fisher_tensors.png',dpi=220,bbox_inches='tight'); plt.close(fig)

# Fig 11: universal collapse by nD
fig,ax=plt.subplots(figsize=(7.4,4.7))
markers={'H':'o','M':'s','S':'^','T':'D','HM':'P','MS':'X','HMS':'v','ALL':'*'}
for dname in dirs:
    d=main[(main.direction==dname)&(main.theta<=.10)]
    ax.scatter(d.z_D,d.accuracy_empirical,s=20,alpha=.62,marker=markers[dname],label=dname)
xx=np.linspace(0,main[main.theta<=.10].z_D.max()*1.04,300)
ax.plot(xx,norm.cdf(xx),linewidth=2.2,label='$\\Phi(\\sqrt{2nD_R})$')
ax.set_xlabel('$\\sqrt{2n D(P,\\mathcal{R}_{\\leftrightarrow})}$')
ax.set_ylabel('Direction accuracy')
ax.set_ylim(.45,1.02)
ax.set_title('Multiple normal mechanisms collapse onto information distance')
ax.grid(alpha=.2); ax.legend(frameon=False,ncol=3,fontsize=8)
fig.tight_layout(); fig.savefig(f'{OUT}/fig11_multi_normal_collapse.png',dpi=220); plt.close(fig)

# Fig 12: predictor errors
ps=pred_summary[pred_summary.scope=='local_theta_le_0.10']
fig,ax=plt.subplots(figsize=(6.8,4.3))
labels=['Raw $\\theta\\sqrt{n}$','Fisher $\\theta\\sqrt{nI}$','Exact $\\sqrt{2nD_R}$']
vals=[ps[ps.predictor=='pred_raw'].MAE.iloc[0],ps[ps.predictor=='pred_fisher'].MAE.iloc[0],ps[ps.predictor=='pred_D'].MAE.iloc[0]]
ax.bar(labels,vals)
ax.set_ylabel('Mean absolute error in accuracy')
ax.set_title('Metric correction restores cross-regime comparability')
ax.tick_params(axis='x',labelrotation=12); ax.grid(axis='y',alpha=.2)
fig.tight_layout(); fig.savefig(f'{OUT}/fig12_metric_comparison.png',dpi=220); plt.close(fig)

# Fig 13: expert transfer matrix
fig,ax=plt.subplots(figsize=(5.5,4.7))
im=ax.imshow(transfer,vmin=.45,vmax=1.0,cmap='viridis')
ax.set_xticks(range(4),pure); ax.set_yticks(range(4),pure)
ax.set_xlabel('Readout / expert direction'); ax.set_ylabel('True normal direction')
ax.set_title('Equal-scale normal directions require direction-matched readouts')
for i in range(4):
    for j in range(4):
        ax.text(j,i,f'{transfer[i,j]*100:.1f}%',ha='center',va='center',fontsize=9,
                color='white' if transfer[i,j]>.72 else 'black')
fig.colorbar(im,ax=ax,label='Direction accuracy')
fig.tight_layout(); fig.savefig(f'{OUT}/fig13_expert_transfer.png',dpi=220); plt.close(fig)

# summary
summary={
    'base_swap_error':swap_err,
    'base_normal_cov_max_error':float(np.max(np.abs(base_cov-np.eye(4)))),
    'local_snr_vs_zD_slope':k,
    'local_snr_vs_zD_R2':r2,
    'tangent_accuracy_mean':tan_df.accuracy.mean(),
    'tangent_accuracy_sd':tan_df.accuracy.std(ddof=1),
    'expert_diag_mean':np.mean(np.diag(transfer)),
    'expert_offdiag_mean':np.mean(transfer[~np.eye(4,dtype=bool)]),
}
for _,r in ps.iterrows():
    summary[r.predictor+'_MAE_local']=r.MAE
    summary[r.predictor+'_corr_local']=r.corr
pd.DataFrame([summary]).to_csv(f'{OUT}/cg004_summary.csv',index=False)

print('SUMMARY')
print(pd.DataFrame([summary]).to_string(index=False))
print('\nPREDICTION')
print(pred_summary.to_string(index=False))
print('\nFISHER')
print(fisher_df[['nuisance','eig_min','eig_max','condition_number','max_abs_offdiag']].to_string(index=False))
print('\nTRANSFER')
print(transfer_df.to_string())
print('\nTANGENT')
print(tan_df.groupby('nuisance').accuracy.agg(['mean','std']).to_string())
