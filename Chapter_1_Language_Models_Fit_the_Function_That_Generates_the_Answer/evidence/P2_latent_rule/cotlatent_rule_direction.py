import sys,math,random,json,numpy as np,torch
sys.path.insert(0,'/mnt/data');import cotlatent as c
random.seed(250933);np.random.seed(250933);torch.manual_seed(250933);torch.set_num_threads(5)
m=c.M();m.load_state_dict(torch.load('/mnt/data/cotlatent.pt',map_location='cpu'));m.eval()

def fwd(ids,patch=None,capture=False):
 patch=patch or {};x=m.p(m.e(ids));caps=[]
 for li,b in enumerate(m.bs):
  B,T,D=x.shape;h=b.h;dh=b.dh;u=b.n1(x);q=b.q(u).view(B,T,h,dh).transpose(1,2);k=b.k(u).view(B,T,h,dh).transpose(1,2);v=b.v(u).view(B,T,h,dh).transpose(1,2);sc=q@k.transpose(-2,-1)/math.sqrt(dh);sc=sc.masked_fill(torch.triu(torch.ones(T,T,dtype=torch.bool),1),-1e9);att=torch.softmax(sc,-1);hc=att@v;attn=b.o(hc.transpose(1,2).reshape(B,T,D));mid=x+attn;mlp=b.f2(torch.nn.functional.gelu(b.f1(b.n2(mid))));out=mid+mlp
  pp=patch.get(li)
  if pp and 'out' in pp:out[:,pp['pos'],:]=pp['out'].to(out)
  if capture:caps.append({'out':out.detach()})
  x=out
 z=m.l(m.n(x));return (z,caps) if capture else z
@torch.no_grad()
def get(meta,patch=None):
 ids=torch.tensor(c.prompt(meta,3))[None,:];z,h=fwd(ids,patch,True);return torch.softmax(z[0,-1],-1),h
rows=[]
for _ in range(2200):
 _,_,meta=c.ex(3);p,h=get(meta)
 if int(p.argmax())==meta['chain'][0]:rows.append({'meta':meta,'b':meta['b'],'start':meta['start'],'target':meta['chain'][0],'p':p,'h':h})
train=rows[:1200];test=rows[1200:1700];pos=[2,3,4,5]
# mean L0 contextual evidence state for each rule; shape 4x64
cent={}
for b in range(c.N):
 z=torch.cat([r['h'][0]['out'][:,pos,:] for r in train if r['b']==b],0)
 cent[b]=z.mean(0,keepdim=True)
# between-rule centroid rank/eigen fractions
C=np.stack([cent[b][0].numpy().reshape(-1) for b in range(c.N)])
C=C-C.mean(0,keepdims=True);sv=np.linalg.svd(C,compute_uv=False);var=sv**2;frac=(var/var.sum()).tolist()
@torch.no_grad()
def run(alpha,random_dir=False):
 vals=[]
 for i,r in enumerate(test):
  rb=r['b'];db=(rb+1+(i%4))%c.N
  if random_dir:
   # wrong label-pair direction, deterministic and distinct
   a=(rb+2)%c.N; d=(db+2)%c.N
   delta=cent[d]-cent[a]
  else: delta=cent[db]-cent[rb]
  new=r['h'][0]['out'][:,pos,:]+alpha*delta
  z,_=get(r['meta'],{0:{'pos':pos,'out':new}});op=(r['start']+db)%c.N;rt=r['target']
  vals.append([int(z.argmax()==rt),int(z.argmax()==op),float(z[rt]-r['p'][rt]),float(z[op]-r['p'][op])])
 A=np.asarray(vals);return {'n':len(vals),'recipient_accuracy':float(A[:,0].mean()),'operator_accuracy':float(A[:,1].mean()),'delta_recipient_p':float(A[:,2].mean()),'delta_operator_p':float(A[:,3].mean())}
out={'centroid_singular_variance_fraction':frac,'alphas':{},'wrong_direction_control':{}}
for a in [0.25,0.5,0.75,1.0,1.25,1.5]:out['alphas'][str(a)]=run(a,False)
for a in [0.5,1.0,1.5]:out['wrong_direction_control'][str(a)]=run(a,True)
json.dump(out,open('/mnt/data/cotlatent_rule_direction.json','w'),indent=2);print(json.dumps(out,indent=2))
