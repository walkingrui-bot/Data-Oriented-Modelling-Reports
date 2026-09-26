
import sys,random,json,numpy as np,torch
sys.path.insert(0,'/mnt/data'); import cotstep as c
from collections import defaultdict
random.seed(260002);torch.manual_seed(260002)
m=c.M();m.load_state_dict(torch.load('/mnt/data/cotstep.pt',map_location='cpu'));m.eval()
def pref(meta):return c.prompt(meta,8)+meta['chain'][:3]
@torch.no_grad()
def get(meta,patch=None):
    log,h=m(torch.tensor(pref(meta))[None,:],True,patch);return torch.softmax(log[0,-1],-1),h
b=defaultdict(lambda:defaultdict(list))
for _ in range(8000):
    _,_,meta=c.ex(8);p,h=get(meta);tg=meta['chain'][3]
    if int(p.argmax())==tg:b[tuple(meta['chain'][:3])][tg].append((meta,p,h,tg))
pairs=[]
for pr,bt in b.items():
    ts=list(bt)
    if len(ts)<2:continue
    loc=[]
    for i in range(len(ts)):
      for j in range(i+1,len(ts)):
        for _ in range(3):loc.append((random.choice(bt[ts[i]]),random.choice(bt[ts[j]])))
    random.shuffle(loc)
    pairs += [(pr,)+x for x in loc[:5]]
print('prefix',len(set(x[0] for x in pairs)),'pairs',len(pairs))
@torch.no_grad()
def patch(r,d,kind):
    P=len(c.prompt(r[0],8));pos=list(range(P,P+3));pa={}
    for li in [1,2]:
        z={'pos':pos}
        if kind in ('K','KV'):z['k']=d[2][li]['k'][:,:,pos,:]
        if kind in ('V','KV'):z['v']=d[2][li]['v'][:,:,pos,:]
        pa[li]=z
    return get(r[0],pa)[0]
out={}
for kind in ['K','V','KV']:
    per=defaultdict(list)
    for pr,r,d in pairs:
        q=patch(r,d,kind);rt=r[3];dt=d[3];base=r[1]
        per[pr].append((int(int(q.argmax())!=rt),int(int(q.argmax())==dt),float(q[rt]-base[rt]),float(q[dt]-base[dt])))
    vals=[]
    for pr,arr in per.items():
        A=np.array(arr); vals.append(A.mean(0))
    M=np.array(vals).mean(0)
    out[kind]={'prefixes':len(vals),'flip':float(M[0]),'donor_argmax':float(M[1]),'d_rec_p':float(M[2]),'d_donor_p':float(M[3])}
print(json.dumps(out,indent=2));json.dump(out,open('/mnt/data/cotfreedom_kv_control.json','w'),indent=2)
