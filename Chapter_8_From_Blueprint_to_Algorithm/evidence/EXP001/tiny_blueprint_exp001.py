# TINY BLUEPRINT EXP001
# Reproducible synthetic experiment: context -> explicit blueprint -> executable answer
# Seed: 20261006
#
# It intentionally uses an order-invariant context encoder and exact enumeration
# over the 12 possible blueprints.
#
# Run with: python tiny_blueprint_exp001.py

import math, random, itertools
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

SEED=20261006
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)

OPS=["ADD","SUB","MAX"]
RULES=list(itertools.permutations(range(3)))
tokens=["<PAD>"]+[f"G{i}" for i in range(3)]+[f"R{i}" for i in range(6)]+[f"O{i}" for i in range(2)]+[f"S{i}" for i in range(2)]+[f"X{i}" for i in range(10)]+[f"Y{i}" for i in range(10)]+[f"D{i}" for i in range(5)]
stoi={t:i for i,t in enumerate(tokens)}

def parity_of_perm(p):
    return sum(1 for i in range(3) for j in range(i+1,3) if p[i]>p[j])%2

def make_example(g,r,o,s,x,y,d):
    op=RULES[r][g]
    arg=o ^ parity_of_perm(RULES[r])
    style=s ^ int(g==2)
    ctx=[f"G{g}",f"R{r}",f"O{o}",f"S{s}",f"X{x}",f"Y{y}",f"D{d}"]
    random.shuffle(ctx)
    return [stoi[t] for t in ctx], (op,arg,style), {"x":x,"y":y}

class TinyBlueprintNet(nn.Module):
    def __init__(self,vocab_size,emb=24,hidden=48,bp_emb=12):
        super().__init__()
        self.tok=nn.Embedding(vocab_size,emb)
        self.enc=nn.Sequential(nn.Linear(emb,hidden),nn.Tanh(),nn.Linear(hidden,hidden),nn.Tanh())
        self.op_head=nn.Linear(hidden,3)
        self.op_emb=nn.Embedding(3,bp_emb)
        self.arg_head=nn.Sequential(nn.Linear(hidden+bp_emb,hidden),nn.Tanh(),nn.Linear(hidden,2))
        self.arg_emb=nn.Embedding(2,bp_emb)
        self.style_head=nn.Sequential(nn.Linear(hidden+2*bp_emb,hidden),nn.Tanh(),nn.Linear(hidden,2))
    def encode(self,x):
        return self.enc(self.tok(x).mean(1))
    def forward_teacher(self,x,yop,yarg):
        h=self.encode(x)
        lo=self.op_head(h)
        la=self.arg_head(torch.cat([h,self.op_emb(yop)],-1))
        ls=self.style_head(torch.cat([h,self.op_emb(yop),self.arg_emb(yarg)],-1))
        return lo,la,ls
    @torch.no_grad()
    def distribution(self,x):
        if x.ndim==1:x=x[None,:]
        h=self.encode(x)
        po=F.softmax(self.op_head(h),-1)[0]
        rows=[]
        for o in range(3):
            ot=torch.tensor([o])
            pa=F.softmax(self.arg_head(torch.cat([h,self.op_emb(ot)],-1)),-1)[0]
            for a in range(2):
                at=torch.tensor([a])
                ps=F.softmax(self.style_head(torch.cat([h,self.op_emb(ot),self.arg_emb(at)],-1)),-1)[0]
                for s in range(2):
                    rows.append(((o,a,s),float(po[o]*pa[a]*ps[s])))
        return sorted(rows,key=lambda z:z[1],reverse=True)

examples=[]
for g,r,o,s in itertools.product(range(3),range(6),range(2),range(2)):
    for _ in range(40):
        examples.append(make_example(g,r,o,s,random.randrange(10),random.randrange(10),random.randrange(5)))
random.shuffle(examples)
n=len(examples); a=int(.8*n); b=int(.9*n)
train,val,test=examples[:a],examples[a:b],examples[b:]

def pack(ex):
    X=torch.tensor([e[0] for e in ex])
    yo=torch.tensor([e[1][0] for e in ex])
    ya=torch.tensor([e[1][1] for e in ex])
    ys=torch.tensor([e[1][2] for e in ex])
    return X,yo,ya,ys
X,yo,ya,ys=pack(train); Xv,yov,yav,ysv=pack(val); Xt,yot,yat,yst=pack(test)

m=TinyBlueprintNet(len(tokens))
opt=torch.optim.AdamW(m.parameters(),lr=5e-3,weight_decay=1e-4)
for epoch in range(160):
    idx=torch.randperm(len(X))
    for i in range(0,len(X),128):
        j=idx[i:i+128]
        lo,la,ls=m.forward_teacher(X[j],yo[j],ya[j])
        loss=F.cross_entropy(lo,yo[j])+F.cross_entropy(la,ya[j])+F.cross_entropy(ls,ys[j])
        opt.zero_grad(); loss.backward(); opt.step()

def acc(X,yo,ya,ys):
    with torch.no_grad():
        h=m.encode(X); po=m.op_head(h).argmax(-1)
        pa=m.arg_head(torch.cat([h,m.op_emb(po)],-1)).argmax(-1)
        ps=m.style_head(torch.cat([h,m.op_emb(po),m.arg_emb(pa)],-1)).argmax(-1)
        return ((po==yo)&(pa==ya)&(ps==ys)).float().mean().item()
print("params",sum(p.numel() for p in m.parameters()))
print("test exact blueprint accuracy",acc(Xt,yot,yat,yst))
print("top exact distribution",m.distribution(Xt[0])[:5])
