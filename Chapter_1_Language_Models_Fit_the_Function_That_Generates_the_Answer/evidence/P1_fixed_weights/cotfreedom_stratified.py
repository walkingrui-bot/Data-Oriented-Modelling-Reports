
import sys,random,json,numpy as np,torch
sys.path.insert(0,'/mnt/data'); import cotstep as c
from collections import defaultdict
random.seed(260001); np.random.seed(260001); torch.manual_seed(260001)
m=c.M();m.load_state_dict(torch.load('/mnt/data/cotstep.pt',map_location='cpu'));m.eval()
def pref(meta):return c.prompt(meta,8)+meta['chain'][:3]
@torch.no_grad()
def get(meta,patch=None):
    log,h=m(torch.tensor(pref(meta))[None,:],True,patch);return torch.softmax(log[0,-1],-1),h
@torch.no_grad()
def patch(rec,don):
    P=len(c.prompt(rec[0],8));pos=list(range(P,P+3))
    pa={li:{'pos':pos,'k':don[2][li]['k'][:,:,pos,:]} for li in [1,2]}
    return get(rec[0],pa)[0]
b=defaultdict(lambda:defaultdict(list))
for _ in range(12000):
    _,_,meta=c.ex(8);p,h=get(meta);tg=meta['chain'][3]
    if int(p.argmax())==tg:
        b[tuple(meta['chain'][:3])][tg].append((meta,p,h,tg))
pairs=[]
for pref0,bytg in b.items():
    ts=list(bytg)
    if len(ts)<2:continue
    local=[]
    for i in range(len(ts)):
        for j in range(i+1,len(ts)):
            for _ in range(min(4,len(bytg[ts[i]]),len(bytg[ts[j]]))):
                r=random.choice(bytg[ts[i]]); d=random.choice(bytg[ts[j]])
                local.append((r,d))
    random.shuffle(local);pairs += [(pref0,)+x for x in local[:8]]
print('prefixes',len(set(x[0] for x in pairs)),'pairs',len(pairs))
per=defaultdict(lambda:{'n':0,'flip':0,'don':0,'drec':[],'ddon':[],'scratch':[],'map':[]})
allrows=[]
for pr,r,d in pairs:
    q=patch(r,d);rt=r[3];dt=d[3];base=r[1]
    P=len(c.prompt(r[0],8)); a=r[2][1]['att'][0,:,-1,:].numpy()
    scratch=float(a[:,P:P+3].sum(-1).mean()); mapm=float(a[:,2:12].sum(-1).mean())
    z={'prefix':pr,'flip':int(int(q.argmax())!=rt),'don':int(int(q.argmax())==dt),
       'drec':float(q[rt]-base[rt]),'ddon':float(q[dt]-base[dt]),'scratch':scratch,'map':mapm}
    allrows.append(z);u=per[pr];u['n']+=1;u['flip']+=z['flip'];u['don']+=z['don'];u['drec'].append(z['drec']);u['ddon'].append(z['ddon']);u['scratch'].append(scratch);u['map'].append(mapm)
perout=[]
for pr,u in per.items():
    perout.append({'prefix':pr,'n':u['n'],'flip':u['flip']/u['n'],'donor':u['don']/u['n'],
                   'drec':float(np.mean(u['drec'])),'ddon':float(np.mean(u['ddon'])),
                   'scratch_attn':float(np.mean(u['scratch'])),'map_attn':float(np.mean(u['map']))})
# equal-prefix mean
agg={k:float(np.mean([x[k] for x in perout])) for k in ['flip','donor','drec','ddon','scratch_attn','map_attn']}
# pair-level correlation
corr=float(np.corrcoef([x['scratch'] for x in allrows],[x['ddon'] for x in allrows])[0,1])
perout=sorted(perout,key=lambda x:x['ddon'],reverse=True)
out={'n_prefixes':len(perout),'n_pairs':len(allrows),'equal_prefix_mean':agg,'corr_scratch_attn_vs_donor_shift':corr,'top_prefixes':perout[:10],'bottom_prefixes':perout[-10:]}
print(json.dumps(out,indent=2));json.dump(out,open('/mnt/data/cotfreedom_stratified.json','w'),indent=2)
