
import sys,random,json,numpy as np,torch
sys.path.insert(0,'/mnt/data'); import cotstep as c
random.seed(250925);torch.manual_seed(250925)
m=c.M();m.load_state_dict(torch.load('/mnt/data/cotstep.pt',map_location='cpu'));m.eval()
def pref(meta,t=3):
    return c.prompt(meta,8)+meta['chain'][:t]
@torch.no_grad()
def get(meta,t=3,patch=None):
    log,hs=m(torch.tensor(pref(meta,t))[None,:],True,patch);return torch.softmax(log[0,-1],-1),hs
# collect baseline-correct examples, bucket by exact visible scratch prefix
b={}
for _ in range(3000):
    _,_,meta=c.ex(8);p,h=get(meta); tg=meta['chain'][3]
    if int(p.argmax())==tg:b.setdefault(tuple(meta['chain'][:3]),[]).append((meta,p,h,tg))
pairs=[]
for arr in b.values():
    for i in range(len(arr)):
        for j in range(i+1,len(arr)):
            if arr[i][3]!=arr[j][3]:
                pairs.append((arr[i],arr[j]));break
        if len(pairs)>=200:break
    if len(pairs)>=200:break
print('pairs',len(pairs))
@torch.no_grad()
def patchrun(rec,don,layers,kind,which='all'):
    meta=rec[0]; dh=don[2]; P=len(c.prompt(meta,8)); positions=list(range(P,P+3)) if which=='all' else [P+2]
    patch={}
    for li in layers:
        x={'pos':positions}
        if kind in ('K','KV'):x['k']=dh[li]['k'][:,:,positions,:]
        if kind in ('V','KV'):x['v']=dh[li]['v'][:,:,positions,:]
        patch[li]=x
    return get(meta,3,patch)[0]
out={}
for which in ['last','all']:
  for layers in [[1],[2],[1,2]]:
    for kind in ['K','V','KV']:
      key=f'{which}_L{"".join(map(str,layers))}_{kind}';flip=donor=0;dr=[];dd=[]
      for rec,don in pairs:
        base=rec[1];rt=rec[3];dt=don[3];p=patchrun(rec,don,layers,kind,which)
        flip+=int(int(p.argmax())!=rt);donor+=int(int(p.argmax())==dt);dr.append(float(p[rt]-base[rt]));dd.append(float(p[dt]-base[dt]))
      out[key]={'flip':flip/len(pairs),'donor_argmax':donor/len(pairs),'d_rec_p':float(np.mean(dr)),'d_donor_p':float(np.mean(dd))}
json.dump(out,open('/mnt/data/cotfreedom_patchall.json','w'),indent=2);print(json.dumps(out,indent=2))
