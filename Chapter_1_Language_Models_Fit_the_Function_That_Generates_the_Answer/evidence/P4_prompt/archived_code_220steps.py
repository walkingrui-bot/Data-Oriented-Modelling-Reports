import torch, torch.nn as nn, torch.nn.functional as F, numpy as np, random, json, math

def seed_all(s): torch.manual_seed(s); np.random.seed(s); random.seed(s)
class Block(nn.Module):
    def __init__(self,d=24,h=3):
        super().__init__(); self.h=h; self.dh=d//h
        self.ln1=nn.LayerNorm(d); self.qkv=nn.Linear(d,3*d,bias=False); self.proj=nn.Linear(d,d,bias=False)
        self.ln2=nn.LayerNorm(d); self.ff=nn.Sequential(nn.Linear(d,48),nn.GELU(),nn.Linear(48,d))
    def forward(self,x):
        B,T,D=x.shape; y=self.ln1(x); q,k,v=self.qkv(y).chunk(3,-1)
        def sp(z): return z.view(B,T,self.h,self.dh).transpose(1,2)
        q,k,v=map(sp,(q,k,v)); a=(q@k.transpose(-2,-1))/math.sqrt(self.dh)
        mask=torch.triu(torch.ones(T,T,dtype=torch.bool),1); a=a.masked_fill(mask,-1e9); a=a.softmax(-1)
        y=(a@v).transpose(1,2).contiguous().view(B,T,D); x=x+self.proj(y); x=x+self.ff(self.ln2(x)); return x
class M(nn.Module):
    def __init__(self,V=52,d=24,L=4,T=7):
        super().__init__(); self.tok=nn.Embedding(V,d); self.pos=nn.Embedding(T,d); self.blocks=nn.ModuleList([Block(d,3) for _ in range(L)]); self.ln=nn.LayerNorm(d); self.out=nn.Linear(d,V,bias=False)
    def forward(self,x,inj=None,vec=None,ret=False):
        B,T=x.shape; h=self.tok(x)+self.pos(torch.arange(T))[None]; hs=[h.detach()] if ret else None
        for i,b in enumerate(self.blocks):
            h=b(h)
            if inj==i: h[:,-1,:]=h[:,-1,:]+vec
            if ret: hs.append(h.detach())
        l=self.out(self.ln(h[:,-1])); return (l,hs) if ret else l
BOS,STYLE,NEUT,SEP=0,1,2,3; N=16; CS=4; AS=20; BS=36; V=52; P=4
def bx(style,c):
    b=len(c); pr=torch.where(style[:,None].bool(),torch.full((b,P),STYLE),torch.full((b,P),NEUT)); return torch.cat([torch.full((b,1),BOS),pr,(CS+c)[:,None],torch.full((b,1),SEP)],1)
def batch(b):
    st=torch.randint(0,2,(b,)); c=torch.randint(0,N,(b,)); x=bx(st,c); pa=torch.where(st.bool(),torch.full((b,),.9),torch.full((b,),.1)); y=torch.where(torch.rand(b)<pa,AS+c,BS+c); return x,y
def pp(log,c):
    ar=torch.arange(len(c)); z=torch.stack([log[ar,AS+c],log[ar,BS+c]],1); return z.softmax(1)
def tv(p,q): return .5*(p-q).abs().sum(1)
res=[]
for sd in [0,1,2]:
    seed_all(sd); m=M(); o=torch.optim.AdamW(m.parameters(),lr=8e-3)
    for it in range(220):
        x,y=batch(96); loss=F.cross_entropy(m(x),y); o.zero_grad(); loss.backward(); o.step()
    c=torch.arange(N); n=bx(torch.zeros(N,dtype=torch.long),c); s=bx(torch.ones(N,dtype=torch.long),c)
    with torch.no_grad(): ln,hn=m(n,ret=True); ls,hs=m(s,ret=True)
    sr={'seed':sd,'base_pA':pp(ln,c)[:,0].mean().item(),'style_pA':pp(ls,c)[:,0].mean().item(),'layers':[]}
    est=torch.arange(8); test=torch.arange(8,16); ct=c[test]
    for i in range(4):
        d=(hs[i+1][est,-1]-hn[i+1][est,-1]).mean(0)
        with torch.no_grad():
            pS=pp(m(s[test]),ct); pN=pp(m(n[test]),ct); pI=pp(m(n[test],inj=i,vec=d),ct)
            rt=[]
            for _ in range(10):
                r=torch.randn_like(d); r=r/r.norm()*d.norm(); rt.append(tv(pp(m(n[test],inj=i,vec=r),ct),pS).mean().item())
        sr['layers'].append({'layer':i+1,'norm':d.norm().item(),'pA_inj':pI[:,0].mean().item(),'tv_base_prompt':tv(pN,pS).mean().item(),'tv_inj_prompt':tv(pI,pS).mean().item(),'rand_tv_mean':float(np.mean(rt)),'rand_tv_min':float(np.min(rt))})
    res.append(sr)
print(json.dumps(res,indent=2))
