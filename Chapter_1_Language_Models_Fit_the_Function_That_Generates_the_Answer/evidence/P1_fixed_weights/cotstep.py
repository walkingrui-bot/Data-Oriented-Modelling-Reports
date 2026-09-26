
import math,random,json,time,torch
import torch.nn as nn, torch.nn.functional as F
random.seed(250925); torch.manual_seed(250925); torch.set_num_threads(5)
N=5; PAD,BOS,MAP,Q,A=5,6,7,8,9; STEP0=10; V=18
def ex(n=None):
    n=n or random.randint(1,5); p=list(range(N)); random.shuffle(p); order=list(range(N)); random.shuffle(order); s=random.randrange(N)
    pr=[BOS,MAP]
    for k in order: pr += [k,p[k]]
    pr += [Q,s,STEP0+n-1,A]; cur=s; ch=[]
    for _ in range(n): cur=p[cur]; ch.append(cur)
    seq=pr+ch; return seq,[0]*len(pr)+[1]*len(ch),dict(perm=p,order=order,start=s,n=n,chain=ch)
def batch(bs=256):
    es=[ex() for _ in range(bs)];L=max(len(x[0]) for x in es);x=torch.full((bs,L-1),PAD,dtype=torch.long);y=x.clone();m=torch.zeros((bs,L-1))
    for b,(s,lm,_) in enumerate(es):x[b,:len(s)-1]=torch.tensor(s[:-1]);y[b,:len(s)-1]=torch.tensor(s[1:]);m[b,:len(s)-1]=torch.tensor(lm[1:])
    return x,y,m
class Pos(nn.Module):
    def __init__(self,d):
        super().__init__();pe=torch.zeros(64,d);pos=torch.arange(64).float()[:,None];div=torch.exp(torch.arange(0,d,2).float()*(-math.log(10000)/d));pe[:,0::2]=torch.sin(pos*div);pe[:,1::2]=torch.cos(pos*div);self.register_buffer('pe',pe,persistent=False)
    def forward(self,x):return x+self.pe[:x.shape[1]]
class Bl(nn.Module):
    def __init__(self,d=64,h=4,ff=128):
        super().__init__();self.h=h;self.dh=d//h;self.n1=nn.LayerNorm(d);self.q=nn.Linear(d,d,bias=False);self.k=nn.Linear(d,d,bias=False);self.v=nn.Linear(d,d,bias=False);self.o=nn.Linear(d,d,bias=False);self.n2=nn.LayerNorm(d);self.f1=nn.Linear(d,ff);self.f2=nn.Linear(ff,d)
    def forward(self,x,hook=False,patch=None,li=None):
        b,t,d=x.shape;u=self.n1(x);q=self.q(u).view(b,t,self.h,self.dh).transpose(1,2);k=self.k(u).view(b,t,self.h,self.dh).transpose(1,2);v=self.v(u).view(b,t,self.h,self.dh).transpose(1,2)
        if patch and li in patch:
            p=patch[li];pos=p['pos']
            if 'k' in p:k[:,:,pos,:]=p['k'].to(k)
            if 'v' in p:v[:,:,pos,:]=p['v'].to(v)
        sc=q@k.transpose(-2,-1)/math.sqrt(self.dh);sc=sc.masked_fill(torch.triu(torch.ones(t,t,dtype=torch.bool),1),-1e9);att=F.softmax(sc,-1);hc=att@v;mid=x+self.o(hc.transpose(1,2).reshape(b,t,d));out=mid+self.f2(F.gelu(self.f1(self.n2(mid))))
        h=None if not hook else {nm:z.detach() for nm,z in dict(q=q,k=k,v=v,att=att,resid=x,mid=mid,out=out,hc=hc).items()};return out,h
class M(nn.Module):
    def __init__(self):
        super().__init__();d=64;self.e=nn.Embedding(V,d);self.p=Pos(d);self.bs=nn.ModuleList([Bl() for _ in range(3)]);self.n=nn.LayerNorm(d);self.l=nn.Linear(d,V,bias=False);self.l.weight=self.e.weight
    def forward(self,ids,hook=False,patch=None):
        x=self.p(self.e(ids));hs=[]
        for i,b in enumerate(self.bs):x,h=b(x,hook,patch,i);hs.append(h) if hook else None
        z=self.l(self.n(x));return (z,hs) if hook else z
def prompt(meta,n):
    s=[BOS,MAP]
    for k in meta['order']:s += [k,meta['perm'][k]]
    return s+[Q,meta['start'],STEP0+n-1,A]
@torch.no_grad()
def gen(m,meta,n,patcher=None):
    s=prompt(meta,n);out=[];HH=[]
    for t in range(n):
        patch=patcher(t,s) if patcher else None;log,h=m(torch.tensor(s)[None,:],True,patch);z=int(log[0,-1].argmax());s.append(z);out.append(z);HH.append(h)
    return out,HH
@torch.no_grad()
def ev(m,lens,cases=200):
    R={}
    for n in lens:
        final=tok=exact=oneshot=0
        for _ in range(cases):
            _,_,meta=ex(n);pred,_=gen(m,meta,n);ch=meta['chain'];final+=pred[-1]==ch[-1];tok+=sum(a==b for a,b in zip(pred,ch));exact+=pred==ch
            log=m(torch.tensor(prompt(meta,n))[None,:]);oneshot+=int(log[0,-1].argmax())==ch[-1]
        R[str(n)]={'final':final/cases,'token':tok/(cases*n),'exact':exact/cases,'one_shot_final':oneshot/cases}
    return R
def main():
    m=M();opt=torch.optim.AdamW(m.parameters(),lr=4e-3,weight_decay=.002);t=time.time();hist=[]
    for st in range(1,1201):
        x,y,mask=batch();log=m(x);ce=F.cross_entropy(log.reshape(-1,V),y.reshape(-1),reduction='none').view_as(y);loss=(ce*mask).sum()/mask.sum();opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(m.parameters(),1);opt.step()
        if st%100==0:print(st,round(loss.item(),4),round(time.time()-t,1),flush=True);hist.append([st,float(loss.detach())])
        if st%300==0:print('EV',json.dumps(ev(m,[3,5,8],80)),flush=True)
    torch.save(m.state_dict(),'/mnt/data/cotstep.pt');r=ev(m,[1,2,3,4,5,6,8,10],300);json.dump({'eval':r,'hist':hist},open('/mnt/data/cotstep_eval.json','w'),indent=2);print('FINAL',json.dumps(r),flush=True)
if __name__=='__main__':main()
