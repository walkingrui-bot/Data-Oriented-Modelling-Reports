import numpy as np, pandas as pd, os, math
from scipy.stats import norm
from numpy.polynomial.hermite import hermgauss
import matplotlib.pyplot as plt

OUT='/mnt/data/causal_geometry_005'
os.makedirs(OUT,exist_ok=True)
SEED=20260927
rng=np.random.default_rng(SEED)
RHOS=[0.20,0.50,0.65,0.85]
RADII=np.array([0.08,0.16,0.28,0.42,0.60,0.82])
MC_G=700000
N_ACC=120

raw_dirs={
    'M':np.array([1.,0,0,0]), 'H':np.array([0.,1,0,0]), 'S':np.array([0.,0,1,0]), 'E':np.array([0.,0,0,1]),
    'MH':np.array([1.,1,0,0])/np.sqrt(2), 'MS':np.array([1.,0,1,0])/np.sqrt(2),
    'HE':np.array([0.,1,0,1])/np.sqrt(2), 'MHS':np.array([1.,1,1,0])/np.sqrt(3),
    'ALL':np.ones(4)/2, 'CONFLICT':np.array([1.,-1,1.,1.])/2,
}

def qshape(z): return np.tanh(z*z-1.0)
def fm(x): return np.tanh(x*x-1.0)
def fh(x): return np.tanh(x)

# High-order Gaussian-Hermite quadrature.
GHN=64
nodes,weights=hermgauss(GHN)
GN=np.sqrt(2.0)*nodes
GW=weights/np.sqrt(np.pi)

def logZ(s):
    v=s*qshape(GN); m=np.max(v)
    return float(m+np.log(np.sum(GW*np.exp(v-m))))

def logpdf_joint(rho,beta,e,x,y,logz_s=None):
    bm,bh,bs,be=beta; s0=np.sqrt(1-rho*rho)
    if logz_s is None: logz_s=logZ(bs)
    logpx=-0.5*(x-be*e)**2-0.5*np.log(2*np.pi)
    mu=rho*x+bm*fm(x)
    lscale=np.log(s0)+bh*fh(x)
    scale=np.exp(lscale)
    z=(y-mu)/scale
    lpz=-0.5*z*z-0.5*np.log(2*np.pi)+bs*qshape(z)-logz_s
    return logpx-lscale+lpz

def exact_expectations(rho,beta):
    bm,bh,bs,be=beta; s0=np.sqrt(1-rho*rho)
    lz=logZ(bs)
    # tilted residual quadrature weights
    wz=GW*np.exp(bs*qshape(GN)-lz)
    # grids u,z and binary environment e
    U,Z=np.meshgrid(GN,GN,indexing='ij')
    W=(GW[:,None]*wz[None,:])
    vals=[]; ws=[]
    for ev in (-1.0,1.0):
        X=be*ev+U
        MU=rho*X+bm*fm(X)
        SCALE=s0*np.exp(bh*fh(X))
        Y=MU+SCALE*Z
        E=np.full_like(X,ev)
        lp=logpdf_joint(rho,beta,E,X,Y,lz)
        lq=logpdf_joint(rho,beta,E,Y,X,lz)
        L=lp-lq
        vals.append(L.ravel()); ws.append((0.5*W).ravel())
    llr=np.concatenate(vals); w=np.concatenate(ws)
    w=w/w.sum()
    js=float(np.sum(w*(np.log(2.0)-np.logaddexp(0.0,-llr))))
    kl=float(np.sum(w*llr))
    mu=kl
    var=float(np.sum(w*(llr-mu)**2))
    # Bhattacharyya/Chernoff information; symmetry makes s=1/2 optimal.
    affinity=float(np.sum(w*np.exp(-0.5*llr)))
    ch=float(-np.log(affinity))
    # single-sample Bayes error exact: .5 E_P[min(1, exp(-LLR))]
    pe1=0.5*float(np.sum(w*np.minimum(1.0,np.exp(-llr))))
    return {'JS_exact':js,'KL_P_swap':kl,'LLR_mean':mu,'LLR_var':var,'Chernoff':ch,'single_accuracy':1-pe1}

# Local antisymmetric Fisher matrix analytically under Gaussian baseline via GH quadrature.
def local_G_exact(rho):
    s0=np.sqrt(1-rho*rho)
    U,Z=np.meshgrid(GN,GN,indexing='ij')
    W=GW[:,None]*GW[None,:]
    # e averaged; only E score changes sign with e, squares survive and cross terms with e vanish.
    x=U; y=rho*U+s0*Z
    zf=Z; zr=(x-rho*y)/s0
    aM=fm(x)*zf/s0-fm(y)*zr/s0
    aH=fh(x)*(zf*zf-1)-fh(y)*(zr*zr-1)
    aS=qshape(zf)-qshape(zr)
    # average over e: E coordinate orthogonal to M/H/S due mean e=0
    aE2=(x-y)**2
    A=[aM,aH,aS]
    G=np.zeros((4,4))
    for i in range(3):
        for j in range(3): G[i,j]=np.sum(W*A[i]*A[j])
    G[3,3]=np.sum(W*aE2)
    return G

Gs={rho:local_G_exact(rho) for rho in RHOS}
frows=[]
for rho,G in Gs.items():
    ev=np.linalg.eigvalsh(G)
    row={'rho':rho,'eig_min':ev.min(),'eig_max':ev.max(),'condition_number':ev.max()/ev.min(),
         'max_abs_offdiag':np.max(np.abs(G-np.diag(np.diag(G))))}
    row.update({f'G{i+1}{j+1}':G[i,j] for i in range(4) for j in range(4)})
    frows.append(row)
pd.DataFrame(frows).to_csv(f'{OUT}/cg005_local_fisher.csv',index=False)

# Main exact grid
rows=[]
for rho in RHOS:
    G=Gs[rho]
    for dname,d in raw_dirs.items():
        unit=d/np.sqrt(d@G@d)
        for r in RADII:
            beta=r*unit
            ex=exact_expectations(rho,beta)
            jsq=r*r/8.0
            sd=np.sqrt(ex['LLR_var'])
            acc_m=norm.cdf(np.sqrt(N_ACC)*ex['LLR_mean']/sd) if sd>0 else 1.0
            rows.append({'rho':rho,'direction':dname,'r_fisher':r,
                         'beta_M':beta[0],'beta_H':beta[1],'beta_S':beta[2],'beta_E':beta[3],
                         **ex,'JS_quadratic':jsq,'curvature_ratio':ex['JS_exact']/jsq,
                         'Chernoff_over_JS':ex['Chernoff']/ex['JS_exact'],
                         'accuracy_moment_n120':acc_m,
                         'accuracy_local_fisher_n120':norm.cdf(np.sqrt(2*N_ACC*jsq)),
                         'accuracy_JSlocal_n120':norm.cdf(np.sqrt(2*N_ACC*ex['JS_exact']))})
main=pd.DataFrame(rows)
main.to_csv(f'{OUT}/cg005_main_grid_exact.csv',index=False)

# Mixed interactions beyond quadratic Fisher cross-terms.
interaction=[]
for rho in [0.20,0.65,0.85]:
    G=Gs[rho]
    for dname,d in raw_dirs.items():
        if dname in ['M','H','S','E']: continue
        unit=d/np.sqrt(d@G@d)
        for r in [0.16,0.28,0.42,0.60,0.82]:
            beta=r*unit
            mix=exact_expectations(rho,beta)['JS_exact']
            sum_parts=0.0; sum_quad_parts=0.0
            for j in range(4):
                if abs(beta[j])>1e-14:
                    bj=np.zeros(4); bj[j]=beta[j]
                    sum_parts+=exact_expectations(rho,bj)['JS_exact']
                    sum_quad_parts+=float(bj@G@bj/8.0)
            quad_mix=float(beta@G@beta/8.0)
            exact_inter=mix-sum_parts
            quad_inter=quad_mix-sum_quad_parts
            nonlinear=exact_inter-quad_inter
            interaction.append({'rho':rho,'direction':dname,'r_fisher':r,'JS_mix':mix,
                                'exact_interaction':exact_inter,'quadratic_interaction':quad_inter,
                                'nonlinear_interaction':nonlinear,
                                'nonlinear_relative_to_JS':nonlinear/mix})
inter=pd.DataFrame(interaction)
inter.to_csv(f'{OUT}/cg005_mixed_interactions_exact.csv',index=False)

# Tangent-regime metric transport: beta calibrated once at rho=.65.
Gref=Gs[0.65]; rr=.18
trans=[]
for rho in RHOS:
    G=Gs[rho]
    for dname,d in raw_dirs.items():
        beta=rr*d/np.sqrt(d@Gref@d)
        js=exact_expectations(rho,beta)['JS_exact']
        ref=rr*rr/8.0
        local=float(beta@G@beta/8.0)
        trans.append({'rho':rho,'direction':dname,'JS_exact':js,'JS_ref_metric':ref,'JS_local_metric':local,
                      'abs_err_ref':abs(js-ref),'abs_err_local':abs(js-local)})
transfer=pd.DataFrame(trans)
transfer.to_csv(f'{OUT}/cg005_metric_transfer_exact.csv',index=False)

# Summaries
curv=main.groupby('r_fisher').agg(mean_ratio=('curvature_ratio','mean'),sd_ratio=('curvature_ratio','std'),
                                  min_ratio=('curvature_ratio','min'),max_ratio=('curvature_ratio','max'),
                                  mean_C_over_JS=('Chernoff_over_JS','mean'),sd_C_over_JS=('Chernoff_over_JS','std')).reset_index()
curv.to_csv(f'{OUT}/cg005_curvature_summary_exact.csv',index=False)

pred=[]
for scope,df in [('local_r_le_0.28',main[main.r_fisher<=.28]),('mid_r_le_0.60',main[main.r_fisher<=.60]),('all',main)]:
    for col in ['accuracy_local_fisher_n120','accuracy_JSlocal_n120']:
        pred.append({'scope':scope,'predictor':col,
                     'MAE_vs_LLRmoment':np.mean(np.abs(df.accuracy_moment_n120-df[col])),
                     'RMSE_vs_LLRmoment':np.sqrt(np.mean((df.accuracy_moment_n120-df[col])**2)),
                     'corr':np.corrcoef(df.accuracy_moment_n120,df[col])[0,1]})
pd.DataFrame(pred).to_csv(f'{OUT}/cg005_prediction_summary_exact.csv',index=False)

# Figures
fig,ax=plt.subplots(figsize=(7.4,4.8))
for dname in raw_dirs:
    d=main[main.direction==dname].groupby('r_fisher').curvature_ratio.mean().reset_index()
    ax.plot(d.r_fisher,d.curvature_ratio,marker='o',label=dname)
ax.axhline(1.0,ls='--',lw=1.1)
ax.set_xlabel('Local Fisher radius r'); ax.set_ylabel('Exact JS / quadratic JS')
ax.set_title('Finite-radius bending of causal information paths in SCMs')
ax.grid(alpha=.2); ax.legend(frameon=False,ncol=5,fontsize=8)
fig.tight_layout(); fig.savefig(f'{OUT}/fig14_curvature_paths_exact.png',dpi=220); plt.close(fig)

agg=transfer.groupby('rho')[['abs_err_ref','abs_err_local']].mean().reset_index()
fig,ax=plt.subplots(figsize=(6.8,4.5)); xx=np.arange(len(agg)); w=.32
ax.bar(xx-w/2,agg.abs_err_ref,w,label='Metric frozen at rho=0.65')
ax.bar(xx+w/2,agg.abs_err_local,w,label='Local Fisher metric')
ax.set_xticks(xx,[str(x) for x in agg.rho]); ax.set_xlabel('Tangent baseline correlation rho')
ax.set_ylabel('Mean absolute JS prediction error'); ax.set_title('Metric transport across tangent regimes')
ax.legend(frameon=False); ax.grid(axis='y',alpha=.2)
fig.tight_layout(); fig.savefig(f'{OUT}/fig15_metric_transport_exact.png',dpi=220); plt.close(fig)

fig,ax=plt.subplots(figsize=(7.2,4.6))
for dname in sorted(inter.direction.unique()):
    d=inter[inter.direction==dname].groupby('r_fisher').nonlinear_relative_to_JS.mean().reset_index()
    ax.plot(d.r_fisher,d.nonlinear_relative_to_JS,marker='o',label=dname)
ax.axhline(0,ls='--',lw=1.1)
ax.set_xlabel('Local Fisher radius r'); ax.set_ylabel('Higher-order interaction / exact JS')
ax.set_title('Mixed mechanisms acquire non-quadratic interactions at finite radius')
ax.grid(alpha=.2); ax.legend(frameon=False,ncol=3,fontsize=8)
fig.tight_layout(); fig.savefig(f'{OUT}/fig16_mixed_interactions_exact.png',dpi=220); plt.close(fig)

# prediction breakdown versus moment CLT target
errs=[]
for r,d in main.groupby('r_fisher'):
    errs.append({'r':r,
                 'local':np.mean(np.abs(d.accuracy_moment_n120-d.accuracy_local_fisher_n120)),
                 'JS':np.mean(np.abs(d.accuracy_moment_n120-d.accuracy_JSlocal_n120))})
ed=pd.DataFrame(errs)
fig,ax=plt.subplots(figsize=(7.0,4.5))
ax.plot(ed.r,ed.local,marker='o',label='Local Fisher distance')
ax.plot(ed.r,ed.JS,marker='s',label='Exact JS, local Gaussian mapping')
ax.set_xlabel('Local Fisher radius r'); ax.set_ylabel('MAE vs exact LLR-moment prediction (n=120)')
ax.set_title('A local causal metric has a finite radius of validity')
ax.grid(alpha=.2); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(f'{OUT}/fig17_prediction_breakdown_exact.png',dpi=220); plt.close(fig)

fig,ax=plt.subplots(figsize=(7.0,4.5))
for dname in ['M','H','S','E','ALL','CONFLICT']:
    d=main[main.direction==dname].groupby('r_fisher').Chernoff_over_JS.mean().reset_index()
    ax.plot(d.r_fisher,d.Chernoff_over_JS,marker='o',label=dname)
ax.axhline(1.0,ls='--',lw=1.1)
ax.set_xlabel('Local Fisher radius r'); ax.set_ylabel('Chernoff / JS')
ax.set_title('Locally equivalent divergences separate away from reversibility')
ax.grid(alpha=.2); ax.legend(frameon=False,ncol=3,fontsize=8)
fig.tight_layout(); fig.savefig(f'{OUT}/fig18_global_divergence_split_exact.png',dpi=220); plt.close(fig)

print('Fisher')
print(pd.DataFrame(frows)[['rho','eig_min','eig_max','condition_number','max_abs_offdiag']].to_string(index=False))
print('\nCurvature')
print(curv.to_string(index=False))
print('\nMetric transfer',transfer[['abs_err_ref','abs_err_local']].mean().to_dict())
print('\nHigher-order interactions')
print(inter.groupby('r_fisher').nonlinear_relative_to_JS.agg(['mean','std','min','max']).to_string())
print('\nPrediction errors vs LLR moment')
print(pd.DataFrame(pred).to_string(index=False))
