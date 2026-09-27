import os,json,random,re,hashlib,shutil
from collections import Counter
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader,Dataset
OUT='/mnt/data/tool_chain_006e_sem_evidence';os.makedirs(OUT,exist_ok=True)
SEED=26092781;random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))
SRC='/mnt/data/tool_chain_006d_final_evidence/tool_chain_006d_final_eval.py';source=open(SRC).read();prefix=source.split("OUT='/mnt/data/tool_chain_006d_final_evidence'")[0];ns={};exec(prefix,ns)
Action=ns['Action'];CELLS=ns['CELLS'];KEYS=ns['KEYS'];VALS=ns['VALS'];TOOLS=ns['TOOLS'];NONE=ns['NONE'];D=ns['D'];make_task=ns['make_task'];features=ns['features'];append_exec=ns['append_exec'];emit_json=ns['emit_json'];ok_write=ns['ok_write']
PAT=re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|-?\d+|[A-Za-z_<>]+|[{}\[\]:,]|[^\s]')
def atoks(a):return PAT.findall(emit_json(a))
SPECIAL=['<PAD>','<BOS>','<EOS>','<UNK>'];KC=[NONE]+KEYS;VC=[-1]+VALS;TI={x:i for i,x in enumerate(TOOLS)};KI={x:i for i,x in enumerate(KC)};VI={x:i for i,x in enumerate(VC)}
def build(n_tasks=1800):
 rr=random.Random(SEED+1);X=[];seq=[];lab=[];cnt=Counter()
 def add(lines,a):
  X.append(features(lines));q=atoks(a);seq.append(q);cnt.update(q);lab.append([TI[a.tool],KI[a.k1],KI[a.k2],VI[a.value]])
 for ti in range(n_tasks):
  t=make_task(rr)
  for ci,c in enumerate(CELLS):
   rng=random.Random(SEED+100000+ti*31+ci);lines=[t.request];w=t.init.copy();ctr=0
   for a in t.oracle:
    add(lines,a)
    if a.tool=='DONE':break
    ctr=append_exec(lines,w,a,ctr,rng,c,ti*17+ci)
  if ti%3==0:
   bad=t.target.copy();r2=random.Random(SEED+ti);k=r2.choice(KEYS);bad[k]=(bad[k]+r2.randrange(1,10))%10;diff={kk:{'expected':t.target[kk],'observed':bad[kk]} for kk in KEYS if bad[kk]!=t.target[kk]};l2=[t.request,'STATE '+json.dumps(bad,separators=(',',':'),sort_keys=True),'VERIFY_FAIL '+json.dumps(diff,separators=(',',':'),sort_keys=True)];fix=Action('WRITE',k,value=t.target[k]);add(l2,fix);add(l2+['ACTION '+emit_json(fix),ok_write(k,t.target[k]),'VERIFY_OK'],Action('DONE'))
 vocab=SPECIAL+sorted(cnt);stoi={t:i for i,t in enumerate(vocab)};Y=[]
 for q in seq:Y.append([stoi['<BOS>']]+[stoi.get(x,stoi['<UNK>']) for x in q]+[stoi['<EOS>']])
 return np.stack(X).astype('float32'),Y,np.asarray(lab,np.int64),vocab,stoi,cnt
class DS(Dataset):
 def __init__(self,X,Y,L):self.X=X;self.Y=Y;self.L=L
 def __len__(self):return len(self.Y)
 def __getitem__(self,i):return self.X[i],self.Y[i],self.L[i]
def coll(b):
 X=torch.tensor(np.stack([x for x,_,_ in b]),dtype=torch.float32);L=max(len(y) for _,y,_ in b);inp=torch.zeros((len(b),L-1),dtype=torch.long);tgt=torch.zeros((len(b),L-1),dtype=torch.long);mask=torch.zeros((len(b),L-1),dtype=torch.float32);lab=torch.tensor(np.stack([z for _,_,z in b]),dtype=torch.long)
 for i,(_,y,_) in enumerate(b):n=len(y)-1;inp[i,:n]=torch.tensor(y[:-1]);tgt[i,:n]=torch.tensor(y[1:]);mask[i,:n]=1
 return X,inp,tgt,mask,lab
class Model(nn.Module):
 def __init__(self,d,v,emb=32,ctx=72,hid=96):
  super().__init__();self.emb=nn.Embedding(v,emb,padding_idx=0);self.ctx=nn.Sequential(nn.Linear(d,160),nn.ReLU(),nn.Linear(160,ctx),nn.ReLU());self.h0=nn.Linear(ctx,hid);self.gru=nn.GRU(emb+ctx,hid,batch_first=True);self.out=nn.Linear(hid,v);self.heads=nn.ModuleList([nn.Linear(ctx,5),nn.Linear(ctx,9),nn.Linear(ctx,9),nn.Linear(ctx,11)])
 def forward(self,x,tok):
  c=self.ctx(x);h=torch.tanh(self.h0(c)).unsqueeze(0);e=self.emb(tok);cc=c.unsqueeze(1).expand(-1,e.size(1),-1);z,_=self.gru(torch.cat([e,cc],-1),h);return self.out(z),[h_(c) for h_ in self.heads]
 def start(self,x):c=self.ctx(x);return c,torch.tanh(self.h0(c)).unsqueeze(0)
 def step(self,t,c,h):e=self.emb(t);z,h=self.gru(torch.cat([e,c.unsqueeze(1)],-1),h);return self.out(z[:,-1]),h
X,Y,L,vocab,stoi,cnt=build();ds=DS(X,Y,L);dl=DataLoader(ds,batch_size=768,shuffle=True,collate_fn=coll,num_workers=0)
m=Model(D,len(vocab));opt=torch.optim.AdamW(m.parameters(),lr=3e-3,weight_decay=1e-5)
# inverse-sqrt token frequency, normalized and clipped; PAD gets zero.
f=np.ones(len(vocab),float)
for tok,n in cnt.items():f[stoi[tok]]=n
f[stoi['<EOS>']]=len(Y);f[stoi['<PAD>']]=1e12;w=1/np.sqrt(f);w=w/np.mean(w[1:]);w=np.clip(w,.35,4.0);w[0]=0;cw=torch.tensor(w,dtype=torch.float32)
hist=[]
for ep in range(4):
 m.train();num=den=auxn=0.0
 for x,inp,tgt,mask,lab in dl:
  opt.zero_grad(set_to_none=True);log,heads=m(x,inp);ls=nn.functional.cross_entropy(log.reshape(-1,len(vocab)),tgt.reshape(-1),weight=cw,reduction='none').reshape_as(tgt);seq=(ls*mask).sum()/mask.sum();aux=sum(nn.functional.cross_entropy(heads[j],lab[:,j]) for j in range(4))/4;loss=seq+0.85*aux;loss.backward();nn.utils.clip_grad_norm_(m.parameters(),1.0);opt.step();num+=float((ls*mask).sum().detach());den+=float(mask.sum());auxn+=float(aux.detach())
 hist.append({'seq_weighted':num/den,'aux_batch_mean':auxn/len(dl)});print('EPOCH',ep+1,hist[-1],flush=True)
 torch.save({'state':m.state_dict(),'vocab':vocab,'hist':hist,'D':D,'emb':32,'ctx':72,'hid':96,'seed':SEED,'train_actions':len(Y),'token_weights':w.tolist()},OUT+'/policy.pt')
json.dump({'history':hist,'train_actions':len(Y),'vocab_size':len(vocab),'feature_dim':D},open(OUT+'/training_history.json','w'),indent=2)
shutil.copy2(__file__,OUT+'/train_script.py');shutil.copy2(SRC,OUT+'/006d_reader_reference.py')
print('SAVED',len(Y),len(vocab),flush=True)
