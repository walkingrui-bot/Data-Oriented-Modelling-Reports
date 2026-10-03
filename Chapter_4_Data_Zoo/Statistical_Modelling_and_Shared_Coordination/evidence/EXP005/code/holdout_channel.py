import importlib.util, numpy as np, pandas as pd, torch, math
from torch import nn
spec=importlib.util.spec_from_file_location('exp','/mnt/data/INTERNAL_COORDINATION_005/code/experiment.py')
# Avoid executing main loop by reading definitions before rows=[]
code=open('/mnt/data/INTERNAL_COORDINATION_005/code/experiment.py').read().split('rows=[]; grads=[]; trajs=[]')[0]
ns={}; exec(code,ns)
Model=ns['Model']; Y_base=ns['Y_base']; tr_idx=ns['tr_idx']; te_idx=ns['te_idx']
torch.set_num_threads(1)

def loss5(m,b):
    ls=[]
    for i in range(5):
        z=m.encode(b[:,i,:],i)
        for j in range(5): ls.append(((m.decode(z,j)-b[:,j,:])**2).mean())
    return torch.stack(ls).mean()
def focus5(m,b):
    ls=[]
    z5=m.encode(b[:,5,:],5)
    for j in range(5): ls.append(((m.decode(z5,j)-b[:,j,:])**2).mean())
    for i in range(5):
        zi=m.encode(b[:,i,:],i); ls.append(((m.decode(zi,5)-b[:,5,:])**2).mean())
    ls.append(((m.decode(z5,5)-b[:,5,:])**2).mean())
    return torch.stack(ls).mean()
def evalfocus(m):
    b=torch.tensor(Y_base[te_idx],dtype=torch.float32); vals=[]
    with torch.no_grad():
        z5=m.encode(b[:,5,:],5)
        for j in range(5): vals.append(torch.sqrt(((m.decode(z5,j)-b[:,j,:])**2).mean()).item())
        for i in range(5):
            zi=m.encode(b[:,i,:],i); vals.append(torch.sqrt(((m.decode(zi,5)-b[:,5,:])**2).mean()).item())
    return float(np.mean(vals))
rows=[]
for mode in ['affine','neural']:
  for seed in range(5):
    torch.manual_seed(seed); np.random.seed(seed); rng=np.random.default_rng(seed+500)
    m=Model(mode); opt=torch.optim.Adam(m.parameters(),lr=0.008)
    # Train shared reality only on channels 0..4
    for st in range(300):
      ids=rng.choice(tr_idx,size=64,replace=False); b=torch.tensor(Y_base[ids],dtype=torch.float32)
      opt.zero_grad(); l=loss5(m,b); l.backward(); opt.step()
    # freeze world and old channel modules, reset channel 5 module so it is truly new
    if mode=='affine': A=ns['AffineAdapter']
    else: A=ns['ResidualChannelNet']
    m.cin[5]=A(); m.cout[5]=A()
    for p in m.parameters(): p.requires_grad=False
    params=list(m.cin[5].parameters())+list(m.cout[5].parameters())
    for p in params: p.requires_grad=True
    opt=torch.optim.Adam(params,lr=0.01)
    pre=evalfocus(m)
    for st in range(250):
      ids=rng.choice(tr_idx,size=64,replace=False); b=torch.tensor(Y_base[ids],dtype=torch.float32)
      opt.zero_grad(); l=focus5(m,b); l.backward(); opt.step()
    post=evalfocus(m)
    rows.append({'mode':mode,'seed':seed,'new_channel_pre_rmse':pre,'new_channel_post_rmse':post,'improvement_pct':100*(pre-post)/pre})
    print(mode,seed,pre,post)
pd.DataFrame(rows).to_csv('/mnt/data/INTERNAL_COORDINATION_005/results/holdout_channel.csv',index=False)
print(pd.DataFrame(rows).groupby('mode').median(numeric_only=True))
