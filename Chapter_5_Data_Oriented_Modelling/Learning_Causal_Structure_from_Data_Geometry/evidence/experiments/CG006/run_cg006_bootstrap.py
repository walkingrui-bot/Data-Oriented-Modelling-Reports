import numpy as np, pandas as pd, os
from scipy.stats import skew,kurtosis,spearmanr
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupShuffleSplit
OUT='/mnt/data/causal_geometry_006'; rng=np.random.default_rng(260928)
D=pd.read_csv(f'{OUT}/cg006_practical_features.csv')
gcols=[c for c in D if c.startswith('g') and c[1:].isdigit()]; scols=[c for c in D if c.startswith('s') and c[1:].isdigit()]
cal=D[D.split=='cal']; GSS=GroupShuffleSplit(n_splits=1,test_size=.28,random_state=11); itr,iva=next(GSS.split(cal,groups=cal.group)); tr=cal.iloc[itr]
trr=tr.drop_duplicates('group'); router=RandomForestClassifier(n_estimators=300,min_samples_leaf=4,max_features=.65,class_weight='balanced',random_state=3).fit(trr[scols],trr.family)
FAMS=['REV','ANM','HET','NG','ENV','PNL']; experts={}
for fam in FAMS[1:]:
 z=tr[tr.family==fam]; experts[fam]=make_pipeline(StandardScaler(),LogisticRegression(C=.7,max_iter=3000)).fit(z[gcols],z.left_is_cause)
classes=list(router.classes_); cmap={c:i for i,c in enumerate(classes)}
def predict(gap,sym):
 one=pd.DataFrame([{**{f'g{k}':gap[k] for k in range(len(gap))},**{f's{k}':sym[k] for k in range(len(sym))}}])
 rp=router.predict_proba(one[scols])[0]; num=0; mass=0
 for fam,mod in experts.items():
  w=rp[cmap[fam]]; num+=w*mod.predict_proba(one[gcols])[0,1]; mass+=w
 return num/(mass+1e-12),rp[cmap['REV']]
def gen(fam,n,seed):
 rg=np.random.default_rng(seed); E=rg.choice([-1.,1.],size=n); a=rg.uniform(.55,1.35); noise=rg.uniform(.55,1.05)
 if fam=='REV': X=rg.normal(size=n); Y=a*X+noise*rg.normal(size=n); E=rg.choice([-1.,1.],size=n)
 elif fam=='ANM': X=rg.normal(size=n); Y=a*X+rg.uniform(.45,.9)*np.tanh(1.4*X)+noise*rg.normal(size=n)
 elif fam=='HET': X=rg.normal(size=n); Y=a*X+noise*np.exp(rg.uniform(.45,.8)*np.tanh(X))*rg.normal(size=n)
 elif fam=='NG': X=rg.laplace(size=n)/np.sqrt(2); Y=a*X+noise*rg.laplace(size=n)/np.sqrt(2)
 elif fam=='ENV': X=rg.uniform(.8,1.4)*E+rg.normal(size=n); Y=a*X+noise*rg.normal(size=n)
 elif fam=='PNL': X=rg.normal(size=n); Z=a*X+noise*rg.normal(size=n); Y=Z+rg.uniform(.45,.75)*np.tanh(1.3*Z)
 elif fam=='MIX':
  X=rg.uniform(.55,1.15)*E+rg.normal(size=n); eps=rg.laplace(size=n)/np.sqrt(2); Y=a*X+rg.uniform(.2,.65)*np.tanh(X)+noise*np.exp(rg.uniform(.25,.65)*np.tanh(X))*eps
 X=(X-X.mean())/(X.std()+1e-12); Y=(Y-Y.mean())/(Y.std()+1e-12); return X,Y,E
def poly(x,y,d):
 A=np.column_stack([np.ones(len(x))]+[x**k for k in range(1,d+1)]); c=np.linalg.lstsq(A,y,rcond=None)[0]; r=y-A@c; return r,c,np.mean(r*r)
def binned(x,r,bins=8):
 qs=np.unique(np.quantile(x,np.linspace(0,1,bins+1))); idx=np.digitize(x,qs[1:-1],right=True); M=[];S=[];N=[]
 for b in range(len(qs)-1):
  z=r[idx==b]
  if len(z)>=8:M.append(z.mean());S.append(z.std()+1e-12);N.append(len(z))
 if len(M)<3:return 0.,0.
 M=np.array(M);S=np.array(S);N=np.array(N);w=N/N.sum(); return float(np.sum(w*(M-np.sum(w*M))**2)/(np.var(r)+1e-12)),float(np.std(S)/(np.mean(S)+1e-12))
def envstab(x,y,E):
 C=[];V=[]
 for ev in (-1.,1.): r,c,_=poly(x[E==ev],y[E==ev],3);C.append(c);V.append(np.var(r))
 C=np.array(C); return float(np.linalg.norm(C[0]-C[1])/(np.linalg.norm(C.mean(0))+1e-8)),float(np.std(V)/(np.mean(V)+1e-12))
def dftr(x,y,E):
 r3,c,m3=poly(x,y,3);r1,c,m1=poly(x,y,1);eta,fib=binned(x,r3);ec,ev=envstab(x,y,E)
 return np.array([eta,fib,abs(spearmanr(x,np.abs(r3)).statistic),abs(spearmanr(x,r3*r3).statistic),abs(skew(r3)),abs(kurtosis(r3,fisher=True)),max(0,(m1-m3)/(m1+1e-12)),ec,ev,m3])
def pack(x,y,E):
 a=dftr(x,y,E);b=dftr(y,x,E);g=a-b; sym=np.concatenate([np.minimum(a,b),np.maximum(a,b),np.abs(g)])
 mm=[]
 for z in (x,y):mm += [abs(skew(z)),abs(kurtosis(z,fisher=True)),abs(z[E==1].mean()-z[E==-1].mean()),abs(z[E==1].std()-z[E==-1].std())]
 m1=np.array(mm[:4]);m2=np.array(mm[4:]);return g,np.concatenate([sym,np.minimum(m1,m2),np.maximum(m1,m2)])
rows=[]
for fam in ['ANM','HET','NG','ENV','PNL','MIX','REV']:
 for j in range(3):
  X,Y,E=gen(fam,700,int(rng.integers(1e9)));calls=[];ps=[];rvs=[]
  for b in range(10):
   ii=rng.integers(0,len(X),len(X));g,s=pack(X[ii],Y[ii],E[ii]);p,rv=predict(g,s);ps.append(p);rvs.append(rv);calls.append(1 if p>=.8 and rv<.4 else (-1 if p<=.2 and rv<.4 else 0))
  rows.append({'family':fam,'rep':j,'mean_p_left_cause':np.mean(ps),'sd_p':np.std(ps),'mean_p_reversible':np.mean(rvs),'true_call_fraction':np.mean(np.array(calls)==1),'wrong_call_fraction':np.mean(np.array(calls)==-1),'unresolved_fraction':np.mean(np.array(calls)==0)})
B=pd.DataFrame(rows);B.to_csv(f'{OUT}/cg006_bootstrap_stability.csv',index=False)
S=B.groupby('family').agg(mean_true_call=('true_call_fraction','mean'),mean_wrong_call=('wrong_call_fraction','mean'),mean_unresolved=('unresolved_fraction','mean'),median_sd_p=('sd_p','median'),mean_p_rev=('mean_p_reversible','mean')).reset_index();S.to_csv(f'{OUT}/cg006_bootstrap_summary.csv',index=False);print(S.to_string(index=False))
