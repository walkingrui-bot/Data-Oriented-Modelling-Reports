import sys,math,random,json,numpy as np,torch
sys.path.insert(0,'/mnt/data');import cotlatent as c
random.seed(250931);torch.manual_seed(250931);torch.set_num_threads(5)
m=c.M();m.load_state_dict(torch.load('/mnt/data/cotlatent.pt',map_location='cpu'));m.eval()

def fwd(ids,patch=None,capture=False):
 patch=patch or {};x=m.p(m.e(ids));caps=[]
 for li,b in enumerate(m.bs):
  B,T,D=x.shape;h=b.h;dh=b.dh;u=b.n1(x);q=b.q(u).view(B,T,h,dh).transpose(1,2);k=b.k(u).view(B,T,h,dh).transpose(1,2);v=b.v(u).view(B,T,h,dh).transpose(1,2)
  sc=q@k.transpose(-2,-1)/math.sqrt(dh);sc=sc.masked_fill(torch.triu(torch.ones(T,T,dtype=torch.bool),1),-1e9);att=torch.softmax(sc,-1);hc=att@v;attn=b.o(hc.transpose(1,2).reshape(B,T,D));mid=x+attn;mlp=b.f2(torch.nn.functional.gelu(b.f1(b.n2(mid))));out=mid+mlp
  pp=patch.get(li); 
  if pp and 'out' in pp: out[:,pp['pos'],:]=pp['out'].to(out)
  if capture:caps.append({'out':out.detach()})
  x=out
 z=m.l(m.n(x));return (z,caps) if capture else z

def get(meta,patch=None):
 ids=torch.tensor(c.prompt(meta,3))[None,:];z,h=fwd(ids,patch,True);return torch.softmax(z[0,-1],-1),h
rows=[]
for _ in range(700):
 _,_,meta=c.ex(3);p,h=get(meta)
 if int(p.argmax())==meta['chain'][0]:rows.append({'meta':meta,'b':meta['b'],'start':meta['start'],'target':meta['chain'][0],'p':p,'h':h})
ops=[]
for i,rec in enumerate(rows[:400]):
 cand=[d for d in rows if d['b']!=rec['b'] and d['start']!=rec['start']]
 if cand:ops.append((rec,cand[(i*31)%len(cand)]))
@torch.no_grad()
def metr(pos):
 vals=[]
 for rec,don in ops:
  patch={0:{'pos':pos,'out':don['h'][0]['out'][:,pos,:]}}
  z,_=get(rec['meta'],patch);rt=rec['target'];op=(rec['start']+don['b'])%c.N;down=don['target'];base=rec['p']
  vals.append([int(z.argmax()!=rt),int(z.argmax()==op),int(z.argmax()==down),float(z[op]-base[op]),float(z[rt]-base[rt])])
 A=np.asarray(vals);return {'n':len(vals),'flip':float(A[:,0].mean()),'operator':float(A[:,1].mean()),'donor_own':float(A[:,2].mean()),'delta_operator_p':float(A[:,3].mean()),'delta_recipient_p':float(A[:,4].mean())}
R={'x1':[2],'y1':[3],'x2':[4],'y2_final':[5],'first_pair':[2,3],'second_pair':[4,5],'all_evidence':[2,3,4,5]}
out={k:metr(v) for k,v in R.items()};json.dump(out,open('/mnt/data/cotlatent_position.json','w'),indent=2);print(json.dumps(out,indent=2))
