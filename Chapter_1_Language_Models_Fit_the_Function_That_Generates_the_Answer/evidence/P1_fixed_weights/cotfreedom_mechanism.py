
import sys, math, random, json, numpy as np, torch
sys.path.insert(0,'/mnt/data')
import cotstep as c
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score

random.seed(250925); np.random.seed(250925); torch.manual_seed(250925)
m=c.M(); m.load_state_dict(torch.load('/mnt/data/cotstep.pt',map_location='cpu')); m.eval()

def prefix(meta,n,t): # t true scratch tokens already written
    s=c.prompt(meta,n)+meta['chain'][:t]
    return s

@torch.no_grad()
def get(meta,n,t,patch=None):
    ids=torch.tensor(prefix(meta,n,t))[None,:]
    log,hs=m(ids,True,patch)
    p=torch.softmax(log[0,-1],-1)
    return p,hs

# 1) collect fixed-position task-conditioned write states at t=3 on n=8
rows=[]
for i in range(1000):
    _,_,meta=c.ex(8)
    p,hs=get(meta,8,3)
    cur=meta['chain'][2]; target=meta['chain'][3]
    rows.append((meta,cur,target,p,hs))

def effrank(X):
    X=np.asarray(X,float); X=X-X.mean(0,keepdims=True)
    if X.shape[0]<3:return 0.0
    C=(X.T@X)/(X.shape[0]-1)
    tr=np.trace(C); den=np.sum(C*C)
    return float(tr*tr/den) if den>1e-14 else 0.0

layer_stats=[]
for li in range(3):
    K=[];Vv=[];R=[]; y=[]; cur=[]
    for meta,cu,tg,p,hs in rows:
        h=hs[li]
        K.append(h['k'][0,:,-1,:].reshape(-1).numpy())
        Vv.append(h['v'][0,:,-1,:].reshape(-1).numpy())
        R.append(h['out'][0,-1].numpy())
        y.append(tg);cur.append(cu)
    # within-visible-token effective rank (same token + same position, only task context differs)
    er={}
    for nm,X in [('K',K),('V',Vv),('R',R)]:
        vals=[]
        for s in range(c.N):
            idx=[i for i,z in enumerate(cur) if z==s]
            vals.append(effrank([X[i] for i in idx]))
        er[nm]=float(np.mean(vals))
    # 5-fold next-symbol linear probe
    probes={}
    sk=StratifiedKFold(5,shuffle=True,random_state=250925)
    for nm,X in [('K',K),('V',Vv),('R',R)]:
        X=np.asarray(X); yy=np.asarray(y); acc=[]
        for tr,te in sk.split(X,yy):
            clf=make_pipeline(StandardScaler(),LogisticRegression(max_iter=600,C=.5))
            clf.fit(X[tr],yy[tr]);acc.append(accuracy_score(yy[te],clf.predict(X[te])))
        probes[nm]=float(np.mean(acc))
    layer_stats.append({'layer':li,'within_token_effrank':er,'next_symbol_probe_acc':probes})

# token-only baseline
yy=np.array([r[2] for r in rows]); xx=np.array([r[1] for r in rows])
base=[]
sk=StratifiedKFold(5,shuffle=True,random_state=250925)
for tr,te in sk.split(xx,yy):
    # majority next target for each current symbol in train
    table={}
    for s in range(c.N):
        ys=yy[tr][xx[tr]==s]
        table[s]=int(np.bincount(ys,minlength=c.N).argmax()) if len(ys) else 0
    pred=np.array([table[z] for z in xx[te]]);base.append((pred==yy[te]).mean())
token_base=float(np.mean(base))

# 2) attention read freedom across reasoning steps
read=[]
for t in range(0,8):
    sums=[{'neff':[],'map_mass':[],'scratch_mass':[]} for _ in range(3)]
    for i in range(100):
        _,_,meta=c.ex(8); p,hs=get(meta,8,t)
        T=len(prefix(meta,8,t))
        map_pos=list(range(2,12)) # 5 mapping pairs
        scratch_pos=list(range(16,T))
        for li,h in enumerate(hs):
            a=h['att'][0,:,-1,:].numpy() # H,T
            for head in range(a.shape[0]):
                q=a[head]; H=-np.sum(q*np.log(np.clip(q,1e-12,1))); sums[li]['neff'].append(np.exp(H))
                sums[li]['map_mass'].append(q[map_pos].sum())
                sums[li]['scratch_mass'].append(q[scratch_pos].sum() if scratch_pos else 0)
    read.append({'t':t,'layers':[ {k:float(np.mean(v)) for k,v in d.items()} for d in sums ]})

# 3) causal donor patch: same visible 3-token scratch prefix, different true next target
# keep only baseline-correct next predictions
buckets={}
for r in rows:
    meta,cur,tg,p,hs=r
    pref=tuple(meta['chain'][:3])
    if int(p.argmax())==tg:
        buckets.setdefault(pref,[]).append(r)
pairs=[]
for pref,arr in buckets.items():
    for i in range(len(arr)):
        for j in range(i+1,len(arr)):
            if arr[i][2]!=arr[j][2]:
                pairs.append((arr[i],arr[j]));break
        if len(pairs)>=100:break
    if len(pairs)>=100:break

@torch.no_grad()
def patched_probs(rec,don,layers,kind):
    meta=rec[0]; dh=don[4]; pos_idx=len(prefix(meta,8,3))-1
    patch={}
    for li in layers:
        p={'pos':[pos_idx]}
        if kind in ('K','KV'): p['k']=dh[li]['k'][:,:,-1:,:]
        if kind in ('V','KV'): p['v']=dh[li]['v'][:,:,-1:,:]
        patch[li]=p
    return get(meta,8,3,patch)[0]

patch_results={}
conditions=[]
for layers in [[0],[1],[2],[1,2]]:
    for kind in ['K','V','KV']:
        key=f"L{''.join(map(str,layers))}_{kind}"; n=flip=donwin=0; drec=[];ddon=[]
        for rec,don in pairs:
            rp=rec[3]; rt=rec[2]; dt=don[2]
            pp=patched_probs(rec,don,layers,kind); n+=1
            flip+=int(int(pp.argmax())!=rt); donwin+=int(int(pp.argmax())==dt)
            drec.append(float(pp[rt]-rp[rt])); ddon.append(float(pp[dt]-rp[dt]))
        patch_results[key]={'n':n,'flip_rate':flip/max(1,n),'donor_target_argmax_rate':donwin/max(1,n),
                            'delta_recipient_p':float(np.mean(drec)) if drec else 0,
                            'delta_donor_p':float(np.mean(ddon)) if ddon else 0}

out={'n_rows':len(rows),'token_only_probe_acc':token_base,'layer_stats':layer_stats,'read_freedom':read,
     'n_same_visible_prefix_donor_pairs':len(pairs),'patch_results':patch_results}
json.dump(out,open('/mnt/data/cotfreedom_mechanism.json','w'),indent=2)
print(json.dumps(out,indent=2))
