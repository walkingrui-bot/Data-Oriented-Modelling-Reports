import torch, math, json, random
import numpy as np
from dataclasses import dataclass

torch.set_num_threads(1)

DT=torch.float32

def seed_all(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)

class MLPEnc(torch.nn.Module):
    def __init__(self, d_in, hidden, latent=3):
        super().__init__()
        self.net=torch.nn.Sequential(torch.nn.Linear(d_in,hidden,dtype=DT),torch.nn.Tanh(),torch.nn.Linear(hidden,latent,dtype=DT))
    def forward(self,x): return self.net(x)

class TriangleCore(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.diag=torch.nn.Parameter(torch.ones(3,dtype=DT))
        self.edge=torch.nn.Parameter(0.08*torch.randn(6,dtype=DT))
        self.bias=torch.nn.Parameter(torch.zeros(3,dtype=DT))
    def matrix(self):
        e=self.edge; W=torch.diag(self.diag)
        W=W.clone()
        W[0,1]=e[0]; W[1,0]=e[1]; W[1,2]=e[2]; W[2,1]=e[3]; W[2,0]=e[4]; W[0,2]=e[5]
        return W
    def forward(self,h): return torch.tanh(h@self.matrix().T+self.bias)

class Model(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.enc=torch.nn.ModuleList([MLPEnc(3,10),MLPEnc(3,10),MLPEnc(16,18)])
        self.core=TriangleCore()
        self.dec=torch.nn.ModuleList([
            torch.nn.Linear(3,3,dtype=DT),
            torch.nn.Linear(3,3,dtype=DT),
            torch.nn.Linear(3,16,dtype=DT)])
    def representations(self, xs):
        return [self.core(self.enc[i](xs[i])) for i in range(3)]
    def predict(self, xs):
        rs=self.representations(xs)
        out=[]
        for i,r in enumerate(rs):
            row=[]
            for j in range(3):
                y=self.dec[j](r)
                if j==1: y=torch.softmax(y,dim=-1)
                elif j==2: y=torch.sigmoid(y)
                row.append(y)
            out.append(row)
        return rs,out

def make_data(seed=123,n_train=128,n_test=64):
    g=torch.Generator().manual_seed(seed)
    ztr=2*torch.rand((n_train,2),generator=g,dtype=DT)-1
    zte=2*torch.rand((n_test,2),generator=g,dtype=DT)-1
    # fixed simulator matrices
    Aq=torch.tensor([[1.0,0.35,0.55],[-0.45,1.15,-0.25],[0.65,-0.35,0.9]],dtype=DT)
    ab=torch.tensor([0.1,-0.2,0.05],dtype=DT)
    Bq=torch.tensor([[1.1,-0.5,0.8],[-0.7,1.0,-0.3],[0.2,-0.4,-0.6]],dtype=DT)
    bb=torch.tensor([0.1,-0.1,0.2],dtype=DT)
    # image logit basis: smooth patterns fixed
    grid=torch.linspace(-1,1,4,dtype=DT)
    yy,xx=torch.meshgrid(grid,grid,indexing='ij')
    P1=xx.flatten(); P2=yy.flatten(); P3=(xx*yy).flatten()
    Cq=torch.stack([1.15*P1,1.05*P2,1.4*P3],dim=1)
    cb=(0.25*torch.cos(math.pi*xx)*torch.cos(math.pi*yy)).flatten()
    def gen(z):
        q=torch.stack([z[:,0],z[:,1],z[:,0]*z[:,1]],dim=1)
        A=q@Aq.T+ab
        B=torch.softmax(q@Bq.T+bb,dim=1)
        C=torch.sigmoid(q@Cq.T+cb)
        return q,[A,B,C]
    qtr,xtr=gen(ztr); qte,xte=gen(zte)
    return qtr,xtr,qte,xte

WEIGHTS=[1/3,1/3,1/16]
def pair_losses(out, targets, pairing=None):
    # out[src][tgt], pairing optional list target tensors for each src/tgt pre-permuted
    losses=[]
    for i in range(3):
        row=[]
        for j in range(3):
            targ = targets[j] if pairing is None else pairing[i][j]
            row.append(((out[i][j]-targ)**2).mean())
        losses.append(row)
    return losses

def objective(model,xs, mode='self', shuffled=None):
    rs,out=model.predict(xs)
    pl=pair_losses(out,xs,shuffled)
    if mode=='self': loss=sum(pl[i][i] for i in range(3))/3
    else: loss=sum(pl[i][j] for i in range(3) for j in range(3))/9
    return loss,rs,out,pl

def normalized_alignment(rs):
    R=torch.stack(rs,dim=1) # n,3src,3latent
    # rms within-scene pairwise / global sd of reps
    ds=[]
    for a,b in [(0,1),(0,2),(1,2)]: ds.append(torch.sqrt(((R[:,a]-R[:,b])**2).mean()))
    scale=R.std(dim=(0,1)).mean().clamp_min(1e-12)
    return (torch.stack(ds).mean()/scale).item()

def cross_rmse(pl):
    vals=[torch.sqrt(pl[i][j]).item() for i in range(3) for j in range(3) if i!=j]
    return float(np.mean(vals)), float(np.max(vals))

def self_rmse(pl): return float(np.mean([torch.sqrt(pl[i][i]).item() for i in range(3)]))

def linear_r2(rs,q):
    # mean rep -> q ridge-free least squares with intercept
    r=torch.stack(rs,dim=0).mean(0)
    X=torch.cat([r,torch.ones((r.shape[0],1),dtype=DT)],dim=1)
    beta=torch.linalg.lstsq(X,q).solution
    pred=X@beta
    ss=((q-pred)**2).sum(); st=((q-q.mean(0))**2).sum()
    return float((1-ss/st).item())

def grad_cosines(model,xs):
    # target-modality losses under all sources, gradients wrt core params only
    rs,out=model.predict(xs)
    per=[]
    params=[p for p in model.core.parameters() if p.requires_grad]
    if not params:
        return [float('nan')]*3
    for j in range(3):
        L=sum(((out[i][j]-xs[j])**2).mean() for i in range(3))/3
        g=torch.autograd.grad(L,params,retain_graph=True,allow_unused=True)
        v=torch.cat([gg.reshape(-1) for gg in g if gg is not None])
        per.append(v)
    cs=[]
    for a,b in [(0,1),(0,2),(1,2)]:
        va,vb=per[a],per[b]
        den=va.norm()*vb.norm()
        cs.append(float((va@vb/den).item()) if den>1e-15 else float('nan'))
    return cs

def set_freeze(model,freeze):
    if freeze=='core':
        for p in model.core.parameters(): p.requires_grad=False
    elif freeze=='encoders':
        for p in model.enc.parameters(): p.requires_grad=False
    elif freeze=='decoders':
        for p in model.dec.parameters(): p.requires_grad=False
    elif freeze=='interfaces':
        for p in model.enc.parameters(): p.requires_grad=False
        for p in model.dec.parameters(): p.requires_grad=False

def train_one(seed,pre=250,bind=450,lr=0.02,variant='switch',freeze=None):
    seed_all(seed)
    qtr,xtr,qte,xte=make_data()
    model=Model()
    opt=torch.optim.Adam(model.parameters(),lr=lr)
    trace=[]
    def rec(step,phase):
        with torch.no_grad():
            _,rtr,_,pltr=objective(model,xtr,'binding')
            _,rte,_,plte=objective(model,xte,'binding')
            edge=model.core.edge.detach().cpu().numpy().copy()
            diag=model.core.diag.detach().cpu().numpy().copy()
        cos=grad_cosines(model,xtr)
        trace.append(dict(step=step,phase=phase,align_train=normalized_alignment(rtr),align_test=normalized_alignment(rte),cross_train=cross_rmse(pltr)[0],cross_test=cross_rmse(plte)[0],cross_worst_test=cross_rmse(plte)[1],self_test=self_rmse(plte),latent_r2_test=linear_r2(rte,qte),cos_ab=cos[0],cos_ac=cos[1],cos_bc=cos[2],edge_norm=float(np.linalg.norm(edge)),diag_norm=float(np.linalg.norm(diag)),edges=edge.tolist()))
    rec(0,'init')
    if variant=='direct': pre=0
    # phase 1 self
    for t in range(pre):
        opt.zero_grad(); L,_,_,_=objective(model,xtr,'self'); L.backward(); opt.step()
        if t in [0,1,2,4,9,19,49,99,pre-1]: rec(t+1,'self')
    if variant=='self_only':
        rec(pre,'final'); return model,trace
    # freezing at switch
    if freeze:
        set_freeze(model,freeze)
        opt=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=lr)
    # shuffled fixed permutations by source/target; self pairs remain correct
    shuf=None
    if variant=='shuffled':
        rng=np.random.default_rng(seed+9000)
        shuf=[]
        n=xtr[0].shape[0]
        for i in range(3):
            row=[]
            for j in range(3):
                if i==j: row.append(xtr[j])
                else:
                    perm=torch.tensor(rng.permutation(n),dtype=torch.long)
                    row.append(xtr[j][perm])
            shuf.append(row)
    for t in range(bind):
        opt.zero_grad(); L,_,_,_=objective(model,xtr,'binding',shuf); L.backward(); opt.step()
        if t in [0,1,2,3,4,5,9,19,29,49,79,119,199,349,bind-1]: rec(pre+t+1,'binding' if variant!='shuffled' else 'shuffled')
    rec(pre+bind,'final')
    return model,trace

if __name__=='__main__':
    import sys
    for var in ['self_only','direct','switch','shuffled']:
        print('\n',var)
        for s in range(3):
            m,tr=train_one(s,variant=var)
            z=tr[-1]
            print(s,{k:round(z[k],4) for k in ['self_test','cross_test','cross_worst_test','align_test','latent_r2_test']})
