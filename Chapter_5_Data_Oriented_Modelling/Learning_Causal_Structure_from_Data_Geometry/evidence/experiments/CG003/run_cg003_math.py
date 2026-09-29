import numpy as np, pandas as pd, math
from scipy.stats import norm
from numpy.polynomial.hermite import hermgauss
import matplotlib.pyplot as plt

A=0.8
SIGMA=1.0
ALPHAS=np.array([0,.015,.025,.04,.06,.08,.10,.15,.20])
NS=np.array([100,200,400,800,1600,3200])
REPS=300

nodes, weights = hermgauss(200)
def Enorm(f):
    return np.sum(weights*f(np.sqrt(2)*nodes))/np.sqrt(np.pi)

def M(alpha):
    return Enorm(lambda x: np.exp(2*alpha*np.tanh(x)))

def D_R(alpha):
    return 0.5*np.log(M(alpha))

def D_total(alpha):
    return 0.5*(M(alpha)-1.0)

def causal_score(x,y):
    def slope(u,v):
        u=(u-u.mean())/u.std(ddof=0)
        v=(v-v.mean())/v.std(ddof=0)
        X=np.column_stack([np.ones_like(u),u])
        beta=np.linalg.lstsq(X,v,rcond=None)[0]
        r=v-X@beta
        z=np.log(r*r+1e-5)
        h=np.tanh(u)
        return np.cov(h,z,ddof=0)[0,1]/np.var(h)
    return slope(x,y)-slope(y,x)

def sim(alpha,n,reps=REPS,seed=0,tangent=False,delta=0.0):
    rng=np.random.default_rng(seed)
    s=np.empty(reps)
    for i in range(reps):
        x=rng.normal(size=n)
        eps=rng.normal(size=n)
        if tangent:
            y=(A+delta)*x+SIGMA*eps
        else:
            y=A*x+SIGMA*np.exp(alpha*np.tanh(x))*eps
        s[i]=causal_score(x,y)
    mu=s.mean(); sd=s.std(ddof=1)
    return dict(mean=mu,sd=sd,snr=mu/sd,accuracy=(s>0).mean())

# Main grid
rows=[]
for n in NS:
    for j,alpha in enumerate(ALPHAS):
        r=sim(alpha,int(n),seed=10000+int(n)*13+j)
        rows.append(dict(n=int(n),alpha=float(alpha),D_R=D_R(alpha),D_total=D_total(alpha),**r))
grid=pd.DataFrame(rows)
grid['nD_R']=grid.n*grid.D_R
grid['sqrt_nD_R']=np.sqrt(grid['nD_R'])
grid.to_csv('/mnt/data/causal_geometry_003_math/cg003_normal_grid.csv',index=False)

# Fit SNR = k sqrt(nD_R), alpha>0
sub=grid[grid.alpha>0]
k=(sub.sqrt_nD_R*sub.snr).sum()/(sub.sqrt_nD_R**2).sum()
pred=k*sub.sqrt_nD_R
r2=1-((sub.snr-pred)**2).sum()/((sub.snr-sub.snr.mean())**2).sum()
grid['accuracy_from_snr']=norm.cdf(grid.snr)
acc_corr=np.corrcoef(grid.accuracy,grid.accuracy_from_snr)[0,1]
acc_mae=np.mean(np.abs(grid.accuracy-grid.accuracy_from_snr))

# tangent matched-total-KL controls
TARGETS=[.04,.08,.15,.20]
tan=[]
for alpha in TARGETS:
    delta=SIGMA*np.sqrt(2*D_total(alpha))
    for n in [200,800,3200]:
        r=sim(0,n,reps=800,seed=81000+int(alpha*1000)+n,tangent=True,delta=delta)
        tan.append(dict(alpha_match=alpha,n=n,D_total=D_total(alpha),D_R_normal=D_R(alpha),delta=delta,**r))
tan=pd.DataFrame(tan)
tan.to_csv('/mnt/data/causal_geometry_003_math/cg003_tangent_controls.csv',index=False)

# Exact constants
var_h=Enorm(lambda x: np.tanh(x)**2)
I_perp=2*var_h
summary={
    'Var_tanhX':var_h,
    'I_perp':I_perp,
    'snr_k':k,
    'snr_fit_r2':r2,
    'accuracy_phi_corr':acc_corr,
    'accuracy_phi_mae':acc_mae,
    'tangent_accuracy_mean':tan.accuracy.mean(),
    'tangent_accuracy_sd':tan.accuracy.std(ddof=1),
}
for p in [.8,.9,.95,.99]:
    summary[f'nDR_threshold_{int(100*p)}']=(norm.ppf(p)/k)**2
pd.DataFrame([summary]).to_csv('/mnt/data/causal_geometry_003_math/cg003_math_summary.csv',index=False)

# Figure 7: exact normal distance and local quadratic
alphaf=np.linspace(0,.22,200)
dr=np.array([D_R(a) for a in alphaf])
approx=var_h*alphaf**2
fig,ax=plt.subplots(figsize=(7.2,4.5))
ax.plot(alphaf**2,dr,label='Exact $D(P_\\alpha, \\mathcal{R})$')
ax.plot(alphaf**2,approx,'--',label='$\\alpha^2\\,Var[tanh(X)]$')
ax.set_xlabel('$\\alpha^2$')
ax.set_ylabel('KL distance to reversible manifold')
ax.set_title('Local normal distance is quadratic in mechanism strength')
ax.legend(frameon=False)
ax.grid(alpha=.2)
fig.tight_layout(); fig.savefig('/mnt/data/causal_geometry_003_math/fig7_normal_distance.png',dpi=200); plt.close(fig)

# Figure 8: data collapse
fig,ax=plt.subplots(figsize=(7.2,4.5))
for n in NS:
    q=grid[(grid.n==n)&(grid.alpha>0)]
    ax.scatter(q.sqrt_nD_R,q.accuracy,s=26,label=f'n={n}')
xx=np.linspace(0,max(sub.sqrt_nD_R)*1.03,300)
ax.plot(xx,norm.cdf(k*xx),linewidth=2,label=f'$\\Phi({k:.3f}\\sqrt{{nD_R}})$')
ax.set_xlabel('$\\sqrt{n D(P,\\mathcal{R})}$')
ax.set_ylabel('Causal direction accuracy')
ax.set_ylim(.45,1.02)
ax.set_title('Identifiability collapses onto normal information volume')
ax.legend(frameon=False,ncol=2,fontsize=8)
ax.grid(alpha=.2)
fig.tight_layout(); fig.savefig('/mnt/data/causal_geometry_003_math/fig8_information_collapse.png',dpi=200); plt.close(fig)

# Figure 9: matched KL at n=800
nshow=800
normshow=grid[(grid.n==nshow)&(grid.alpha.isin(TARGETS))].sort_values('alpha')
tanshow=tan[tan.n==nshow].sort_values('alpha_match')
fig,ax=plt.subplots(figsize=(7.2,4.5))
ax.plot(normshow.D_total,normshow.accuracy,marker='o',label='Normal deformation: heteroscedastic')
ax.plot(tanshow.D_total,tanshow.accuracy,marker='o',label='Tangent deformation: Gaussian slope')
ax.axhline(.5,linestyle='--',linewidth=1)
ax.set_xlabel('Matched KL change from baseline')
ax.set_ylabel('Causal direction accuracy (n=800)')
ax.set_ylim(.42,1.03)
ax.set_title('Equal distributional change, unequal causal information')
ax.legend(frameon=False)
ax.grid(alpha=.2)
fig.tight_layout(); fig.savefig('/mnt/data/causal_geometry_003_math/fig9_tangent_normal.png',dpi=200); plt.close(fig)

print(pd.DataFrame([summary]).to_string(index=False))
print('\nTangent controls:\n',tan[['alpha_match','n','D_total','delta','accuracy','snr']].to_string(index=False))
