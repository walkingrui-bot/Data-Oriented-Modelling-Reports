import sys, math, random, json, numpy as np, torch
sys.path.insert(0,'/mnt/data')
import cotstep as c
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score

random.seed(250926); np.random.seed(250926); torch.manual_seed(250926); torch.set_num_threads(5)
m=c.M(); m.load_state_dict(torch.load('/mnt/data/cotstep.pt',map_location='cpu')); m.eval()

def fwd(ids, patches=None, capture=False):
    patches=patches or {}
    x=m.p(m.e(ids)); caps=[]
    for li,b in enumerate(m.bs):
        B,T,D=x.shape; h=b.h; dh=b.dh
        resid=x
        u=b.n1(x)
        q=b.q(u).view(B,T,h,dh).transpose(1,2)
        k=b.k(u).view(B,T,h,dh).transpose(1,2)
        v=b.v(u).view(B,T,h,dh).transpose(1,2)
        pp=patches.get(li,{})
        pos=pp.get('pos',[])
        if pos:
            if 'k' in pp: k[:,:,pos,:]=pp['k'].to(k)
            if 'v' in pp: v[:,:,pos,:]=pp['v'].to(v)
        sc=q@k.transpose(-2,-1)/math.sqrt(dh)
        sc=sc.masked_fill(torch.triu(torch.ones(T,T,dtype=torch.bool),1),-1e9)
        att=torch.softmax(sc,-1)
        hc=att@v
        if pos and 'hc' in pp:
            hv=pp['hc'].to(hc)
            if pp.get('head',None) is None: hc[:,:,pos,:]=hv
            else:
                hd=pp['head']; hc[:,hd:hd+1,pos,:]=hv
        attn_out=b.o(hc.transpose(1,2).reshape(B,T,D))
        if pos and 'attn_out' in pp: attn_out[:,pos,:]=pp['attn_out'].to(attn_out)
        mid=resid+attn_out
        mlp_out=b.f2(torch.nn.functional.gelu(b.f1(b.n2(mid))))
        if pos and 'mlp_out' in pp: mlp_out[:,pos,:]=pp['mlp_out'].to(mlp_out)
        out=mid+mlp_out
        if pos and 'out' in pp: out[:,pos,:]=pp['out'].to(out)
        if capture:
            caps.append({'resid':resid.detach(),'u':u.detach(),'q':q.detach(),'k':k.detach(),'v':v.detach(),'att':att.detach(),'hc':hc.detach(),'attn_out':attn_out.detach(),'mid':mid.detach(),'mlp_out':mlp_out.detach(),'out':out.detach()})
        x=out
    logits=m.l(m.n(x))
    return (logits,caps) if capture else logits

def prefix(meta,n=8,t=3): return c.prompt(meta,n)+meta['chain'][:t]
@torch.no_grad()
def get(meta,n=8,t=3,patch=None):
    ids=torch.tensor(prefix(meta,n,t))[None,:]
    log,caps=fwd(ids,patch,capture=True)
    return torch.softmax(log[0,-1],-1),caps

rows=[]
for _ in range(1000):
    _,_,meta=c.ex(8); p,caps=get(meta)
    rows.append(dict(meta=meta,cur=meta['chain'][2],target=meta['chain'][3],p=p,caps=caps,pref=tuple(meta['chain'][:3])))

def flat_stage(row,li,stage):
    z=row['caps'][li][stage]
    if stage in ('q','k','v','hc','att'): return z[0,:,-1,:].reshape(-1).numpy()
    return z[0,-1].reshape(-1).numpy()

stages=['resid','u','q','k','v','att','hc','attn_out','mid','mlp_out','out']
y=np.array([r['target'] for r in rows])
sk=StratifiedKFold(5,shuffle=True,random_state=250926)
probe={}
for li in range(3):
    probe[str(li)]={}
    for st in stages:
        X=np.asarray([flat_stage(r,li,st) for r in rows]); acc=[]
        for tr,te in sk.split(X,y):
            clf=make_pipeline(StandardScaler(),LogisticRegression(max_iter=400,C=.5))
            clf.fit(X[tr],y[tr]); acc.append(accuracy_score(y[te],clf.predict(X[te])))
        probe[str(li)][st]=float(np.mean(acc))

buckets={}
for r in rows:
    if int(r['p'].argmax())==r['target']: buckets.setdefault(r['pref'],[]).append(r)
pairs=[]
for pref,arr in buckets.items():
    local=[]
    for i in range(len(arr)):
        for j in range(len(arr)):
            if i!=j and arr[i]['target']!=arr[j]['target']:
                local.append((arr[i],arr[j]))
                if len(local)>=5: break
        if len(local)>=5: break
    if local: pairs += [(pref,a,b) for a,b in local]
prefs=[]
for p,_,__ in pairs:
    if p not in prefs:prefs.append(p)
prefs=prefs[:60]
pairs=[x for x in pairs if x[0] in prefs]
POS=list(range(len(prefix(rows[0]['meta']))-3,len(prefix(rows[0]['meta']))))

@torch.no_grad()
def run_patch(rec,patch): return get(rec['meta'],patch=patch)[0]

def summarize(stage_specs):
    per=[]
    for pref,rec,don in pairs:
        patch={}
        for spec in stage_specs:
            li,stage=spec[:2]; head=spec[2] if len(spec)>2 else None
            src=don['caps'][li]; pp=patch.setdefault(li,{'pos':POS})
            if stage in ('k','v'): pp[stage]=src[stage][:,:,POS,:]
            elif stage=='hc':
                if head is None: pp['hc']=src['hc'][:,:,POS,:]
                else: pp['hc']=src['hc'][:,head:head+1,POS,:]; pp['head']=head
            else: pp[stage]=src[stage][:,POS,:]
        p=run_patch(rec,patch); rt=rec['target']; dt=don['target']; base=rec['p']
        per.append((pref,int(p.argmax()!=rt),int(p.argmax()==dt),float(p[rt]-base[rt]),float(p[dt]-base[dt])))
    vals=[]
    for pref in prefs:
        z=[x for x in per if x[0]==pref]
        if z: vals.append([np.mean([a[i] for a in z]) for i in range(1,5)])
    A=np.asarray(vals)
    return dict(n_prefix=len(vals),flip=float(A[:,0].mean()),donor_argmax=float(A[:,1].mean()),delta_rec=float(A[:,2].mean()),delta_don=float(A[:,3].mean()))

causal={}
for li in [0,1,2]:
    for st in ['hc','attn_out','mlp_out','out']:
        causal[f'L{li}_{st}']=summarize([(li,st)])
heads={}
for li in [0,1]:
    heads[str(li)]={}
    for hd in range(4): heads[str(li)][str(hd)]=summarize([(li,'hc',hd)])

@torch.no_grad()
def mediation(clamp='k'):
    per=[]
    for pref,rec,don in pairs:
        patch={0:{'pos':POS,'out':don['caps'][0]['out'][:,POS,:]},1:{'pos':POS,clamp:rec['caps'][1][clamp][:,:,POS,:]}}
        p=run_patch(rec,patch);rt=rec['target'];dt=don['target'];base=rec['p']
        per.append((pref,int(p.argmax()!=rt),int(p.argmax()==dt),float(p[rt]-base[rt]),float(p[dt]-base[dt])))
    vals=[]
    for pref in prefs:
        z=[x for x in per if x[0]==pref]
        if z: vals.append([np.mean([a[i] for a in z]) for i in range(1,5)])
    A=np.asarray(vals)
    return dict(n_prefix=len(vals),flip=float(A[:,0].mean()),donor_argmax=float(A[:,1].mean()),delta_rec=float(A[:,2].mean()),delta_don=float(A[:,3].mean()))

med={'donor_L0_out':causal['L0_out'],'donor_L0_out_plus_recipient_L1K_clamp':mediation('k'),'donor_L0_out_plus_recipient_L1V_clamp':mediation('v')}
out=dict(n_rows=len(rows),n_pairs=len(pairs),n_prefix=len(prefs),positions=POS,probe=probe,causal=causal,head_causal=heads,mediation=med)
json.dump(out,open('/mnt/data/cotfreedom_upstream.json','w'),indent=2)
print(json.dumps(out,indent=2))
