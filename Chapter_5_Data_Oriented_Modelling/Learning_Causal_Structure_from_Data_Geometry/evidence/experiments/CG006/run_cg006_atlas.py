import numpy as np, pandas as pd, os, math
from numpy.polynomial.hermite import hermgauss
from sklearn.cluster import KMeans
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge
import matplotlib.pyplot as plt

OUT='/mnt/data/causal_geometry_006'; os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(20260927)
RHOS=[0.35,0.65,0.85]
GHN=40
nodes,weights=hermgauss(GHN); GN=np.sqrt(2)*nodes; GW=weights/np.sqrt(np.pi)

def qshape(z): return np.tanh(z*z-1.0)
def fm(x): return np.tanh(x*x-1.0)
def fh(x): return np.tanh(x)

def logZ(s):
    v=s*qshape(GN); m=np.max(v); return float(m+np.log(np.sum(GW*np.exp(v-m))))

def logpdf_joint(rho,beta,e,x,y,logz_s=None):
    bm,bh,bs,be=beta; s0=np.sqrt(1-rho*rho)
    if logz_s is None: logz_s=logZ(bs)
    logpx=-0.5*(x-be*e)**2-0.5*np.log(2*np.pi)
    mu=rho*x+bm*fm(x)
    lscale=np.log(s0)+bh*fh(x); scale=np.exp(lscale)
    z=(y-mu)/scale
    lpz=-0.5*z*z-0.5*np.log(2*np.pi)+bs*qshape(z)-logz_s
    return logpx-lscale+lpz

def exact_js(rho,beta):
    bm,bh,bs,be=beta; s0=np.sqrt(1-rho*rho); lz=logZ(bs)
    wz=GW*np.exp(bs*qshape(GN)-lz)
    U,Z=np.meshgrid(GN,GN,indexing='ij'); W=GW[:,None]*wz[None,:]
    out=0.0
    for ev in (-1.,1.):
        X=be*ev+U; MU=rho*X+bm*fm(X); SCALE=s0*np.exp(bh*fh(X)); Y=MU+SCALE*Z
        E=np.full_like(X,ev)
        lp=logpdf_joint(rho,beta,E,X,Y,lz); lq=logpdf_joint(rho,beta,E,Y,X,lz); L=lp-lq
        out += 0.5*np.sum(W*(np.log(2.)-np.logaddexp(0.,-L)))
    return float(out)

def local_G(rho):
    s0=np.sqrt(1-rho*rho); U,Z=np.meshgrid(GN,GN,indexing='ij'); W=GW[:,None]*GW[None,:]
    x=U; y=rho*U+s0*Z; zf=Z; zr=(x-rho*y)/s0
    A=[fm(x)*zf/s0-fm(y)*zr/s0,
       fh(x)*(zf*zf-1)-fh(y)*(zr*zr-1),
       qshape(zf)-qshape(zr)]
    G=np.zeros((4,4))
    for i in range(3):
        for j in range(3): G[i,j]=np.sum(W*A[i]*A[j])
    G[3,3]=np.sum(W*(x-y)**2)
    return G

def sample_x(n, rmax=.9, rmin=.02):
    u=rng.normal(size=(n,4)); u/=np.linalg.norm(u,axis=1,keepdims=True)
    # slightly overrepresent finite radii, but preserve local points
    r=rmin+(rmax-rmin)*rng.beta(1.6,1.25,size=n)
    return u*r[:,None]

def phi_local(dx,degree=2):
    # raw monomials through requested degree using sklearn for consistency
    pf=PolynomialFeatures(degree=degree,include_bias=True)
    return pf.fit_transform(dx)

def fit_local_models(X,y,centers,degree,k_neigh):
    models=[]
    for c in centers:
        dist=np.linalg.norm(X-c,axis=1)
        idx=np.argsort(dist)[:k_neigh]
        d=X[idx]-c
        h=max(np.median(dist[idx])*1.4,0.06)
        w=np.exp(-(dist[idx]/h)**2)
        pf=PolynomialFeatures(degree=degree,include_bias=True)
        F=pf.fit_transform(d)
        sw=np.sqrt(w)[:,None]
        # tiny ridge stabilises cubic fits only, does not materially bias exact targets
        model=Ridge(alpha=1e-10,fit_intercept=False).fit(F*sw,y[idx]*sw.ravel())
        models.append((c,h,pf,model))
    return models

def predict_soft(models,X,k=3):
    C=np.stack([m[0] for m in models])
    out=[]
    for x in X:
        dd=np.linalg.norm(C-x,axis=1); ii=np.argsort(dd)[:k]
        vals=[]; ww=[]
        for j in ii:
            c,h,pf,mod=models[j]
            val=float(mod.predict(pf.transform((x-c)[None,:]))[0])
            vals.append(val); ww.append(np.exp(-(dd[j]/max(h,1e-6))**2))
        ww=np.array(ww); ww=ww/(ww.sum()+1e-12)
        out.append(float(np.dot(ww,vals)))
    return np.maximum(np.array(out),0.)

allrows=[]; summaries=[]; connection=[]
for rho in RHOS:
    G=local_G(rho); L=np.linalg.cholesky(G)
    # x = L^T beta gives Fisher radius ||x||. beta = L^{-T} x.
    Xtr=sample_x(1350,.9,.012); Xte=sample_x(520,.9,.02)
    Btr=np.linalg.solve(L.T,Xtr.T).T; Bte=np.linalg.solve(L.T,Xte.T).T
    ytr=np.array([exact_js(rho,b) for b in Btr]); yte=np.array([exact_js(rho,b) for b in Bte])
    # origin quadratic is exact local Fisher second order
    p_origin_quad=np.sum(Xte*Xte,axis=1)/8.
    # local origin polynomial fits on r<=.34, tested globally to expose finite-radius limits
    rtr=np.linalg.norm(Xtr,axis=1); loc=rtr<=.36
    pf3=PolynomialFeatures(degree=3,include_bias=True); F3=pf3.fit_transform(Xtr[loc])
    m3=Ridge(alpha=1e-10,fit_intercept=False).fit(F3,ytr[loc]); p_origin_cubic=np.maximum(m3.predict(pf3.transform(Xte)),0.)
    # chart centers chosen in whitened geometry, guaranteeing finite-distance coverage
    km=KMeans(n_clusters=24,random_state=42,n_init=10).fit(Xtr)
    centers=km.cluster_centers_
    qmods=fit_local_models(Xtr,ytr,centers,2,120)
    cmods=fit_local_models(Xtr,ytr,centers,3,220)
    p_atlas_q=predict_soft(qmods,Xte,k=3)
    p_atlas_c=predict_soft(cmods,Xte,k=3)
    # connection proxy: cubic correction learned at origin relative to quadratic
    p3train=np.maximum(m3.predict(pf3.transform(Xtr[loc])),0.)
    qtrain=np.sum(Xtr[loc]*Xtr[loc],axis=1)/8.
    connection.append({'rho':rho,'origin_local_n':int(loc.sum()),
                       'origin_quad_MAE_local':float(np.mean(np.abs(ytr[loc]-qtrain))),
                       'origin_cubic_MAE_local':float(np.mean(np.abs(ytr[loc]-p3train))),
                       'cubic_gain':float(np.mean(np.abs(ytr[loc]-qtrain))/np.mean(np.abs(ytr[loc]-p3train)))})
    for i in range(len(Xte)):
        r=np.linalg.norm(Xte[i])
        allrows.append({'rho':rho,'r':r,'JS_exact':yte[i],
                        'origin_quadratic':p_origin_quad[i],'origin_cubic':p_origin_cubic[i],
                        'atlas_quadratic':p_atlas_q[i],'atlas_cubic':p_atlas_c[i]})
    methods=['origin_quadratic','origin_cubic','atlas_quadratic','atlas_cubic']
    for m in methods:
        summaries.append({'rho':rho,'method':m,'MAE':float(np.mean(np.abs(yte - locals()['p_'+m] if False else yte-yte)))})
    # overwrite with explicit
    summaries[-4:]=[
        {'rho':rho,'method':'origin_quadratic','MAE':float(np.mean(np.abs(yte-p_origin_quad))), 'RMSE':float(np.sqrt(np.mean((yte-p_origin_quad)**2)))},
        {'rho':rho,'method':'origin_cubic','MAE':float(np.mean(np.abs(yte-p_origin_cubic))), 'RMSE':float(np.sqrt(np.mean((yte-p_origin_cubic)**2)))},
        {'rho':rho,'method':'atlas_quadratic','MAE':float(np.mean(np.abs(yte-p_atlas_q))), 'RMSE':float(np.sqrt(np.mean((yte-p_atlas_q)**2)))},
        {'rho':rho,'method':'atlas_cubic','MAE':float(np.mean(np.abs(yte-p_atlas_c))), 'RMSE':float(np.sqrt(np.mean((yte-p_atlas_c)**2)))}]

df=pd.DataFrame(allrows); df.to_csv(f'{OUT}/cg006_atlas_grid.csv',index=False)
sumdf=pd.DataFrame(summaries); sumdf.to_csv(f'{OUT}/cg006_atlas_summary.csv',index=False)
pd.DataFrame(connection).to_csv(f'{OUT}/cg006_connection_proxy.csv',index=False)
# error by radius bin
bins=[0,.2,.4,.6,.75,.91]; labels=['0-.2','.2-.4','.4-.6','.6-.75','.75-.9']
df['r_bin']=pd.cut(df.r,bins=bins,labels=labels,include_lowest=True)
err=[]
for (rho,b),g in df.groupby(['rho','r_bin'],observed=True):
    for m in ['origin_quadratic','origin_cubic','atlas_quadratic','atlas_cubic']:
        err.append({'rho':rho,'r_bin':str(b),'method':m,'MAE':float(np.mean(np.abs(g.JS_exact-g[m])))})
errdf=pd.DataFrame(err); errdf.to_csv(f'{OUT}/cg006_atlas_error_by_radius.csv',index=False)
# Figure atlas MAE by rho
fig,ax=plt.subplots(figsize=(7.5,4.6))
for m in ['origin_quadratic','origin_cubic','atlas_quadratic','atlas_cubic']:
    s=sumdf[sumdf.method==m]; ax.plot(s.rho,s.MAE,marker='o',label=m.replace('_',' '))
ax.set_xlabel('Tangent regime rho'); ax.set_ylabel('MAE for exact causal JS'); ax.set_title('Local charts replace a single global causal ruler'); ax.grid(alpha=.2); ax.legend(frameon=False,fontsize=8)
fig.tight_layout(); fig.savefig(f'{OUT}/fig20_atlas_mae.png',dpi=220); plt.close(fig)
# pooled error vs radius
p=errdf.groupby(['r_bin','method'],observed=True).MAE.mean().reset_index()
fig,ax=plt.subplots(figsize=(7.6,4.8))
for m in ['origin_quadratic','origin_cubic','atlas_quadratic','atlas_cubic']:
    s=p[p.method==m]; ax.plot(s.r_bin,s.MAE,marker='o',label=m.replace('_',' '))
ax.set_xlabel('Fisher radius bin'); ax.set_ylabel('Mean absolute JS error'); ax.set_title('Atlas advantage grows away from the reversible origin'); ax.grid(alpha=.2); ax.legend(frameon=False,fontsize=8)
fig.tight_layout(); fig.savefig(f'{OUT}/fig21_atlas_radius.png',dpi=220); plt.close(fig)
print(sumdf.to_string(index=False))
print('\nconnection proxy')
print(pd.DataFrame(connection).to_string(index=False))
print('\npooled by radius')
print(p.to_string(index=False))
