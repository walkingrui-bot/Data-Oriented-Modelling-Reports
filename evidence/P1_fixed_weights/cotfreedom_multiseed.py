
import sys,random,json,numpy as np,torch
sys.path.insert(0,'/mnt/data'); import cotstep as c
m=c.M();m.load_state_dict(torch.load('/mnt/data/cotstep.pt',map_location='cpu'));m.eval()
def pref(meta): return c.prompt(meta,8)+meta['chain'][:3]
@torch.no_grad()
def get(meta,patch=None):
    log,h=m(torch.tensor(pref(meta))[None,:],True,patch);return torch.softmax(log[0,-1],-1),h
@torch.no_grad()
def patch(rec,don):
    P=len(c.prompt(rec[0],8));pos=list(range(P,P+3))
    pa={li:{'pos':pos,'k':don[2][li]['k'][:,:,pos,:]} for li in [1,2]}
    return get(rec[0],pa)[0]
def run(seed):
    random.seed(seed);torch.manual_seed(seed);b={}
    for _ in range(2500):
        _,_,meta=c.ex(8);p,h=get(meta);tg=meta['chain'][3]
        if int(p.argmax())==tg:b.setdefault(tuple(meta['chain'][:3]),[]).append((meta,p,h,tg))
    diff=[];same=[]
    for arr in b.values():
        for i in range(len(arr)):
            for j in range(i+1,len(arr)):
                if arr[i][3]!=arr[j][3] and len(diff)<100:diff.append((arr[i],arr[j]))
                if arr[i][3]==arr[j][3] and len(same)<100:same.append((arr[i],arr[j]))
            if len(diff)>=100 and len(same)>=100:break
        if len(diff)>=100 and len(same)>=100:break
    def stat(ps):
        if not ps:return {}
        fl=don=0;dr=[];dd=[]
        for r,d in ps:
            q=patch(r,d);rt=r[3];dt=d[3];base=r[1]
            fl+=int(int(q.argmax())!=rt);don+=int(int(q.argmax())==dt)
            dr.append(float(q[rt]-base[rt]));dd.append(float(q[dt]-base[dt]))
        return dict(n=len(ps),flip=fl/len(ps),donor=don/len(ps),drec=float(np.mean(dr)),ddon=float(np.mean(dd)))
    return {'seed':seed,'diff':stat(diff),'same':stat(same)}
out=[run(s) for s in [250925,250926,250927,250928,250929]]
print(json.dumps(out,indent=2));json.dump(out,open('/mnt/data/cotfreedom_multiseed.json','w'),indent=2)
