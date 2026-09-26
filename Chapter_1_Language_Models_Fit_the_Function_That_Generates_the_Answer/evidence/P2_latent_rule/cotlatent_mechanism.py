import sys, math, random, json, numpy as np, torch
sys.path.insert(0,'/mnt/data'); import cotlatent as c
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
random.seed(250930);np.random.seed(250930);torch.manual_seed(250930);torch.set_num_threads(5)
m=c.M();m.load_state_dict(torch.load('/mnt/data/cotlatent.pt',map_location='cpu'));m.eval()

# custom forward with interventions
def fwd(ids,patches=None,capture=False):
    patches=patches or {};x=m.p(m.e(ids));caps=[]
    for li,b in enumerate(m.bs):
        B,T,D=x.shape;h=b.h;dh=b.dh;resid=x;u=b.n1(x);q=b.q(u).view(B,T,h,dh).transpose(1,2);k=b.k(u).view(B,T,h,dh).transpose(1,2);v=b.v(u).view(B,T,h,dh).transpose(1,2)
        pp=patches.get(li,{});pos=pp.get('pos',[])
        if pos:
            if 'k' in pp:k[:,:,pos,:]=pp['k'].to(k)
            if 'v' in pp:v[:,:,pos,:]=pp['v'].to(v)
        sc=q@k.transpose(-2,-1)/math.sqrt(dh);sc=sc.masked_fill(torch.triu(torch.ones(T,T,dtype=torch.bool),1),-1e9);att=torch.softmax(sc,-1);hc=att@v
        if pos and 'hc' in pp:hc[:,:,pos,:]=pp['hc'].to(hc)
        attn=b.o(hc.transpose(1,2).reshape(B,T,D));
        if pos and 'attn_out' in pp:attn[:,pos,:]=pp['attn_out'].to(attn)
        mid=resid+attn;mlp=b.f2(torch.nn.functional.gelu(b.f1(b.n2(mid))));
        if pos and 'mlp_out' in pp:mlp[:,pos,:]=pp['mlp_out'].to(mlp)
        out=mid+mlp
        if pos and 'out' in pp:out[:,pos,:]=pp['out'].to(out)
        if capture:caps.append({nm:z.detach() for nm,z in dict(resid=resid,u=u,q=q,k=k,v=v,att=att,hc=hc,attn_out=attn,mid=mid,mlp_out=mlp,out=out).items()})
        x=out
    z=m.l(m.n(x));return (z,caps) if capture else z

def pr(meta,n=3):return c.prompt(meta,n)
@torch.no_grad()
def get(meta,n=3,patch=None):
    ids=torch.tensor(pr(meta,n))[None,:];z,h=fwd(ids,patch,True);return torch.softmax(z[0,-1],-1),h

# rows before any scratch output; A token fixed at pos 9
rows=[]
for _ in range(1500):
    _,_,meta=c.ex(3);p,h=get(meta,3);rows.append(dict(meta=meta,b=meta['b'],start=meta['start'],target=meta['chain'][0],p=p,h=h))

# rule b probe at A (fixed visible token) and at final evidence token (pos5)
stages=['resid','u','q','k','v','att','hc','attn_out','mid','mlp_out','out']; POS_A=9;POS_E=5

def vec(r,li,st,pos):
    z=r['h'][li][st]
    if st in ('q','k','v','hc','att'):return z[0,:,pos,:].reshape(-1).numpy()
    return z[0,pos].reshape(-1).numpy()
y=np.array([r['b'] for r in rows]);sk=StratifiedKFold(5,shuffle=True,random_state=250930)
probe={'A':{},'Efinal':{}}
for place,pos in [('A',POS_A),('Efinal',POS_E)]:
    for li in range(3):
        probe[place][str(li)]={}
        for st in stages:
            X=np.asarray([vec(r,li,st,pos) for r in rows]);acc=[]
            for tr,te in sk.split(X,y):
                clf=make_pipeline(StandardScaler(),LogisticRegression(max_iter=400,C=.5));clf.fit(X[tr],y[tr]);acc.append(accuracy_score(y[te],clf.predict(X[te])))
            probe[place][str(li)][st]=float(np.mean(acc))

# baseline-correct pool
pool=[r for r in rows if int(r['p'].argmax())==r['target']]
# same-start different-b pairs for A-state answer transfer
same=[]
byS={}
for r in pool:byS.setdefault(r['start'],[]).append(r)
for s,arr in byS.items():
    cnt=0
    for rec in arr:
        for don in arr:
            if rec['b']!=don['b'] and rec['target']!=don['target']:
                same.append((rec,don));cnt+=1
                if cnt>=80:break
        if cnt>=80:break
# diverse donor pairs for operator transfer, recipient/donor starts can differ
ops=[]
for i in range(min(500,len(pool))):
    rec=pool[i]
    candidates=[d for d in pool if d['b']!=rec['b'] and d['start']!=rec['start']]
    if not candidates:continue
    don=candidates[(i*37)%len(candidates)];ops.append((rec,don))

@torch.no_grad()
def patched(rec,don,spec):
    # spec list (li,stage,positions)
    patch={}
    for li,st,pos in spec:
        pp=patch.setdefault(li,{'pos':pos});src=don['h'][li][st]
        if st in ('k','v','hc'): pp[st]=src[:,:,pos,:]
        else: pp[st]=src[:,pos,:]
    z,_=get(rec['meta'],3,patch);return z

def metrics(pairs,spec,operator=False):
    vals=[]
    for rec,don in pairs:
        p=patched(rec,don,spec); base=rec['p']; rt=rec['target']; donor_own=don['target']; op=(rec['start']+don['b'])%c.N
        vals.append(dict(flip=int(int(p.argmax())!=rt),donor_own=int(int(p.argmax())==donor_own),operator=int(int(p.argmax())==op),dr=float(p[rt]-base[rt]),do=float(p[op]-base[op])))
    return {k:float(np.mean([v[k] for v in vals])) for k in vals[0]}

# A contextual state transplant (same start => donor own == donor rule on recipient start)
Apatch={}
for li in range(3):
    for st in ['hc','attn_out','mlp_out','out']:
        Apatch[f'L{li}_{st}']=metrics(same,[(li,st,[POS_A])])

# Evidence-state operator transplant: recipient start stays intact
Epos=[2,3,4,5]
Epatch={}
for li in range(3):
    for st in ['k','v','out']:
        Epatch[f'L{li}_{st}']=metrics(ops,[(li,st,Epos)],operator=True)
# two-layer variants
Epatch['L01_out']=metrics(ops,[(0,'out',Epos),(1,'out',Epos)],operator=True)
Epatch['L12_k']=metrics(ops,[(1,'k',Epos),(2,'k',Epos)],operator=True)
Epatch['L12_v']=metrics(ops,[(1,'v',Epos),(2,'v',Epos)],operator=True)

# mediation: donor L0 evidence out; clamp layer1 evidence K or V back to recipient
@torch.no_grad()
def med(clamp):
    vals=[]
    for rec,don in ops:
        patch={0:{'pos':Epos,'out':don['h'][0]['out'][:,Epos,:]},1:{'pos':Epos,clamp:rec['h'][1][clamp][:,:,Epos,:]}}
        z,_=get(rec['meta'],3,patch);base=rec['p'];rt=rec['target'];op=(rec['start']+don['b'])%c.N
        vals.append(dict(flip=int(int(z.argmax())!=rt),operator=int(int(z.argmax())==op),dr=float(z[rt]-base[rt]),do=float(z[op]-base[op])))
    return {k:float(np.mean([v[k] for v in vals])) for k in vals[0]}
mediation={'donor_L0_evidence_out':Epatch['L0_out'],'plus_recipient_L1K_clamp':med('k'),'plus_recipient_L1V_clamp':med('v')}

out=dict(n_rows=len(rows),n_pool=len(pool),n_same_pairs=len(same),n_operator_pairs=len(ops),probe=probe,A_patch=Apatch,evidence_operator_patch=Epatch,mediation=mediation)
json.dump(out,open('/mnt/data/cotlatent_mechanism.json','w'),indent=2)
print(json.dumps(out,indent=2))
