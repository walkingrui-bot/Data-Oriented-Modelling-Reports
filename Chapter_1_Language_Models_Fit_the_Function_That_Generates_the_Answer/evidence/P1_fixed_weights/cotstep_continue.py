import sys,time,json,torch
sys.path.insert(0,'/mnt/data')
import cotstep_500 as c
import torch.nn.functional as F
m=c.M();m.load_state_dict(torch.load('/mnt/data/cotstep.pt',map_location='cpu'));opt=torch.optim.AdamW(m.parameters(),lr=2e-3,weight_decay=.002);t=time.time()
for st in range(1,301):
 x,y,mask=c.batch();log=m(x);ce=F.cross_entropy(log.reshape(-1,c.V),y.reshape(-1),reduction='none').view_as(y);loss=(ce*mask).sum()/mask.sum();opt.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),1);opt.step()
 if st%100==0:print(st,round(loss.item(),4),round(time.time()-t,1),flush=True)
torch.save(m.state_dict(),'/mnt/data/cotstep.pt');r=c.ev(m,[1,3,5,8],120);json.dump({'eval':r},open('/mnt/data/cotstep_eval2.json','w'),indent=2);print('FINAL',json.dumps(r),flush=True)
