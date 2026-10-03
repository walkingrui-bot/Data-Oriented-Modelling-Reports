import numpy as np,pandas as pd,torch,math
from torch import nn
code=open('/mnt/data/INTERNAL_COORDINATION_005/code/experiment.py').read().split('rows=[]; grads=[]; trajs=[]')[0]
ns={};exec(code,ns)
Model=ns['Model'];Y_base=ns['Y_base'];Y_shift=ns['Y_shift'];tr_idx=ns['tr_idx'];te_idx=ns['te_idx'];bind_loss=ns['bind_loss']
torch.set_num_threads(1)

class DriftState(nn.Module):
    def __init__(self):
        super().__init__(); self.sin=nn.Parameter(torch.zeros(16)); self.bin=nn.Parameter(torch.zeros(16)); self.sout=nn.Parameter(torch.zeros(16)); self.bout=nn.Parameter(torch.zeros(16))
    def enc(self,h): return h*torch.exp(self.sin)+self.bin
    def dec(self,z): return z*torch.exp(self.sout)+self.bout

def encode(m,st,x,c):
    h=m.perc(x);h=m.cin[c](h)
    if c==5:h=st.enc(h)
    return torch.tanh(m.core(h))
def decode(m,st,z,c):
    if c==5:z=st.dec(z)
    return m.gen(m.cout[c](z))
def focus_loss(m,st,b):
    ls=[];z5=encode(m,st,b[:,5,:],5)
    for j in range(6):ls.append(((decode(m,st,z5,j)-b[:,j,:])**2).mean())
    for i in range(5):
      zi=encode(m,st,b[:,i,:],i);ls.append(((decode(m,st,zi,5)-b[:,5,:])**2).mean())
    return torch.stack(ls).mean()
def eval_focus(m,st):
    b=torch.tensor(Y_shift[te_idx],dtype=torch.float32);vals=[]
    with torch.no_grad():
      z5=encode(m,st,b[:,5,:],5)
      for j in range(5):vals.append(torch.sqrt(((decode(m,st,z5,j)-b[:,j,:])**2).mean()).item())
      for i in range(5):
        zi=encode(m,st,b[:,i,:],i);vals.append(torch.sqrt(((decode(m,st,zi,5)-b[:,5,:])**2).mean()).item())
    return float(np.mean(vals))
rows=[]
for seed in range(3):
  torch.manual_seed(seed);np.random.seed(seed);rng=np.random.default_rng(seed+1234)
  m=Model('neural');opt=torch.optim.Adam(m.parameters(),lr=0.008)
  for step in range(300):
    ids=rng.choice(tr_idx,size=64,replace=False);b=torch.tensor(Y_base[ids],dtype=torch.float32)
    opt.zero_grad();l=bind_loss(m,b);l.backward();opt.step()
  for p in m.parameters():p.requires_grad=False
  st=DriftState();opt=torch.optim.Adam(st.parameters(),lr=0.02)
  pre=eval_focus(m,st)
  cal=rng.choice(tr_idx,size=48,replace=False)
  for k in range(150):
    ids=rng.choice(cal,size=48,replace=False);b=torch.tensor(Y_shift[ids],dtype=torch.float32)
    opt.zero_grad();l=focus_loss(m,st,b);l.backward();opt.step()
  post=eval_focus(m,st)
  state_norm=float(torch.sqrt(sum((p.detach()**2).sum() for p in st.parameters())).item())
  rows.append({'seed':seed,'pre_focus_rmse':pre,'state_post_focus_rmse':post,'improvement_pct':100*(pre-post)/pre,'state_norm':state_norm,'state_params':64})
  print(seed,pre,post)
pd.DataFrame(rows).to_csv('/mnt/data/INTERNAL_COORDINATION_005/results/dynamic_state.csv',index=False)
print(pd.DataFrame(rows).median(numeric_only=True))
