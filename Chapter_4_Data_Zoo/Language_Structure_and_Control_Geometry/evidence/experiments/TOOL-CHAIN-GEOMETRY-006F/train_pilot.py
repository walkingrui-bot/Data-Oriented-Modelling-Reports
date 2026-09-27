import os,json,random,re,hashlib,time,sys,shutil
from collections import Counter
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader,TensorDataset

OUT='/mnt/data/tool_chain_006f_evidence'; os.makedirs(OUT,exist_ok=True)
SEED=26092931
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))
SRC='/mnt/data/006d_unpack/tool_chain_006d_final_evidence/tool_chain_006d_final_eval.py'
source=open(SRC).read(); prefix=source.split("OUT='/mnt/data/tool_chain_006d_final_evidence'")[0]; ns={}; exec(prefix,ns)
Action=ns['Action']; CELLS=ns['CELLS']; KEYS=ns['KEYS']; VALS=ns['VALS']; TOOLS=ns['TOOLS']; NONE=ns['NONE']; D=ns['D']; make_task=ns['make_task']; features=ns['features']; append_exec=ns['append_exec']; emit_json=ns['emit_json']
# semantic autoregressive action language: tool -> k1 -> k2 -> value -> EOS
SPECIAL=['<PAD>','<BOS>','<EOS>']
TOOL_T=[f'TOOL_{x}' for x in TOOLS]
K1_T=[f'K1_{x}' for x in [NONE]+KEYS]
K2_T=[f'K2_{x}' for x in [NONE]+KEYS]
V_T=[f'V_{x}' for x in [-1]+VALS]
VOCAB=SPECIAL+TOOL_T+K1_T+K2_T+V_T
stoi={t:i for i,t in enumerate(VOCAB)}

def action_seq(a):
    return [stoi['<BOS>'],stoi[f'TOOL_{a.tool}'],stoi[f'K1_{a.k1}'],stoi[f'K2_{a.k2}'],stoi[f'V_{a.value}'],stoi['<EOS>']]

def seq_action(ids):
    if len(ids)!=4:return None,'length'
    ts=[VOCAB[i] if 0<=i<len(VOCAB) else '' for i in ids]
    if not(ts[0].startswith('TOOL_') and ts[1].startswith('K1_') and ts[2].startswith('K2_') and ts[3].startswith('V_')):return None,'slot'
    tool=ts[0][5:]; k1=ts[1][3:]; k2=ts[2][3:]
    try:v=int(ts[3][2:])
    except:return None,'value'
    a=Action(tool,k1,k2,v)
    # same validity contract as 006D
    if tool=='READ':ok=k1 in KEYS and k2==NONE and v==-1
    elif tool=='READPAIR':ok=k1 in KEYS and k2 in KEYS and k1!=k2 and v==-1
    elif tool=='WRITE':ok=k1 in KEYS and k2==NONE and v in VALS
    elif tool=='CLEAR':ok=k1 in KEYS and k2==NONE and v==-1
    elif tool=='DONE':ok=k1==NONE and k2==NONE and v==-1
    else:ok=False
    return (a,None) if ok else (a,'schema')

class GenPlanner(nn.Module):
    def __init__(self,d,v,emb=48,ctx=160,hid=192):
        super().__init__()
        self.emb=nn.Embedding(v,emb,padding_idx=0)
        self.ctx=nn.Sequential(nn.Linear(d,256),nn.ReLU(),nn.Linear(256,ctx),nn.ReLU())
        self.h0=nn.Linear(ctx,hid)
        self.gru=nn.GRU(emb+ctx,hid,batch_first=True)
        self.out=nn.Linear(hid,v)
    def forward(self,x,tok):
        c=self.ctx(x); h=torch.tanh(self.h0(c)).unsqueeze(0); e=self.emb(tok); cc=c[:,None,:].expand(-1,e.size(1),-1)
        z,_=self.gru(torch.cat([e,cc],-1),h); return self.out(z)
    def start(self,x):
        c=self.ctx(x); return c,torch.tanh(self.h0(c)).unsqueeze(0)
    def step(self,t,c,h):
        e=self.emb(t); z,h=self.gru(torch.cat([e,c[:,None,:]],-1),h); return self.out(z[:,-1]),h


def build_data(n_tasks=6000):
    rr=random.Random(SEED+1); X=[]; Y=[]
    for ti in range(n_tasks):
        t=make_task(rr)
        for ci,cell in enumerate(CELLS):
            rng=random.Random(SEED+100000+ti*17+ci); lines=[t.request]; w=t.init.copy(); ctr=0
            for a in t.oracle:
                X.append(features(lines)); Y.append(action_seq(a))
                if a.tool=='DONE':break
                ctr=append_exec(lines,w,a,ctr,rng,cell,SEED+ti*31+ci)
        if (ti+1)%1000==0:print('BUILD',ti+1,flush=True)
    return np.stack(X).astype('float32'),np.asarray(Y,dtype=np.int64)

@torch.no_grad()
def generate(m,x):
    xt=torch.tensor(x[None,:],dtype=torch.float32); c,h=m.start(xt); cur=torch.tensor([[stoi['<BOS>']]],dtype=torch.long); outs=[]
    # generate exactly four semantic slots; EOS is checked separately
    for pos in range(4):
        log,h=m.step(cur,c,h); i=int(log.argmax(-1)); outs.append(i); cur=torch.tensor([[i]])
    # one extra step for EOS diagnostic
    log,h=m.step(cur,c,h); eos=int(log.argmax(-1))==stoi['<EOS>']
    a,err=seq_action(outs); return a,err,eos,outs

def prefix_pilot(m,n_tasks=350):
    rr=random.Random(SEED+51000); n=exact=valid=eosn=0; sloterr=sch=0
    by={c.name:[0,0] for c in CELLS}
    for ti in range(n_tasks):
        t=make_task(rr)
        for ci,cell in enumerate(CELLS):
            rng=random.Random(SEED+200000+ti*13+ci); lines=[t.request]; w=t.init.copy(); ctr=0
            for oracle in t.oracle:
                a,err,eos,_=generate(m,features(lines)); n+=1; eosn+=eos; valid+=err is None; sloterr+=err in ('length','slot','value'); sch+=err=='schema'; exact+=int(err is None and a.tup()==oracle.tup()); by[cell.name][1]+=1; by[cell.name][0]+=int(err is None and a.tup()==oracle.tup())
                if oracle.tool=='DONE':break
                ctr=append_exec(lines,w,oracle,ctr,rng,cell,SEED+ti*29+ci)
    return {'n':n,'exact':exact/n,'valid':valid/n,'eos':eosn/n,'slot_error':sloterr/n,'schema_error':sch/n,'by_cell':{k:v[0]/v[1] for k,v in by.items()}}

def run_episode(m,t,cell,seed,max_steps=14):
    rng=random.Random(seed); w=t.init.copy(); lines=[t.request]; ctr=0; oi=0; fd=0; perr=0; sch=0; vf=0; recovered=0
    for step in range(max_steps):
        a,err,eos,ids=generate(m,features(lines))
        if err:
            perr+=1; sch+=int(err=='schema'); lines.append('PLANNER_GENERATION_ERROR '+json.dumps({'error':err,'tokens':[VOCAB[i] for i in ids]},separators=(',',':')))
            if perr>=3:break
            continue
        if not fd and a.tup()!=t.oracle[min(oi,len(t.oracle)-1)].tup():fd=step+1
        oi+=1
        if a.tool in ('READ','READPAIR','WRITE','CLEAR'):
            ctr=append_exec(lines,w,a,ctr,rng,cell,seed+step)
        else:
            lines.append('ACTION '+emit_json(a))
            if w==t.target:
                lines.append('VERIFY_OK');return {'ok':1,'first_div':fd,'planner_errors':perr,'schema_errors':sch,'verify_failures':vf,'steps':step+1}
            vf+=1; diff={k:{'expected':t.target[k],'observed':w[k]} for k in KEYS if w[k]!=t.target[k]}; lines+=['STATE '+json.dumps(w,separators=(',',':'),sort_keys=True),'VERIFY_FAIL '+json.dumps(diff,separators=(',',':'),sort_keys=True)]
            if vf>=2:break
    return {'ok':int(w==t.target),'first_div':fd,'planner_errors':perr,'schema_errors':sch,'verify_failures':vf,'steps':max_steps}

def baseline_pilot(m,n_tasks=240):
    rr=random.Random(SEED+52000); tasks=[make_task(rr) for _ in range(n_tasks)]; c=CELLS[0]; rs=[]
    for i,t in enumerate(tasks):rs.append(run_episode(m,t,c,SEED+700000+i))
    return {'n':len(rs),'final_state_accuracy':sum(r['ok'] for r in rs)/len(rs),'planner_error_any':sum(r['planner_errors']>0 for r in rs)/len(rs),'schema_error_any':sum(r['schema_errors']>0 for r in rs)/len(rs),'mean_first_div_failure':float(np.mean([r['first_div'] for r in rs if not r['ok'] and r['first_div']])) if any((not r['ok'] and r['first_div']) for r in rs) else None}

def main():
    X,Y=build_data(6000); print('DATA',X.shape,Y.shape,'D',D,'V',len(VOCAB),flush=True)
    inp=torch.tensor(Y[:,:-1],dtype=torch.long); tgt=torch.tensor(Y[:,1:],dtype=torch.long); xt=torch.tensor(X,dtype=torch.float32)
    ds=TensorDataset(xt,inp,tgt); dl=DataLoader(ds,batch_size=1536,shuffle=True,num_workers=0)
    m=GenPlanner(D,len(VOCAB)); opt=torch.optim.AdamW(m.parameters(),lr=2.5e-3,weight_decay=1e-5); hist=[]
    # position/token weighted loss: semantic slots equal; EOS lighter
    for ep in range(7):
        m.train(); num=den=0.0
        for xb,ib,tb in dl:
            opt.zero_grad(set_to_none=True); log=m(xb,ib); loss=nn.functional.cross_entropy(log.reshape(-1,len(VOCAB)),tb.reshape(-1)); loss.backward(); nn.utils.clip_grad_norm_(m.parameters(),1.0); opt.step(); num+=float(loss.detach())*len(xb); den+=len(xb)
        hist.append(num/den); pil=prefix_pilot(m,120); print('EPOCH',ep+1,'NLL',hist[-1],'PFX',pil['exact'],'VALID',pil['valid'],flush=True)
        torch.save({'state':m.state_dict(),'vocab':VOCAB,'D':D,'emb':48,'ctx':160,'hid':192,'seed':SEED,'history':hist},OUT+'/planner.pt')
    m.eval(); pp=prefix_pilot(m,350); bp=baseline_pilot(m,240)
    gate={'prefix_exact_threshold':0.85,'baseline_final_state_threshold':0.65,'passed':bool(pp['exact']>=0.85 and bp['final_state_accuracy']>=0.65)}
    res={'experiment':'TOOL-CHAIN-GEOMETRY-006F pilot gate','design':'autoregressive semantic planner trained from oracle trajectories; no 006D planner used','seed':SEED,'train_tasks':6000,'train_actions':len(Y),'feature_dim':D,'vocab_size':len(VOCAB),'training_nll':hist,'prefix_pilot':pp,'baseline_pilot_P1_N1':bp,'prospective_gate':gate}
    json.dump(res,open(OUT+'/pilot_gate.json','w'),indent=2); shutil.copy2(__file__,OUT+'/train_pilot.py')
    print('GATE',json.dumps(res),flush=True)
if __name__=='__main__':main()
