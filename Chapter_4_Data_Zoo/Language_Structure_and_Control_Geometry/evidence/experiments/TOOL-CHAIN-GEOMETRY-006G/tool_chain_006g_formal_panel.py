import os,json,random,re,csv,argparse,importlib.util,hashlib
from collections import Counter
import numpy as np
import torch
import torch.nn as nn

ap=argparse.ArgumentParser();ap.add_argument('--panel',type=int,required=True);args=ap.parse_args();PI=args.panel
OUT='/mnt/data/tool_chain_006g_evidence';SEED_D=26092821
spec=importlib.util.spec_from_file_location('g','/mnt/data/tool_chain_006g_train.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
z=torch.load(OUT+'/planner.pt',map_location='cpu');planner=g.GenPlanner(z['D'],len(z['vocab']),z['emb'],z['ctx'],z['hid']);planner.load_state_dict(z['state']);planner.eval()
@torch.no_grad()
def plan(lines):
    x=torch.tensor(g.features(lines)[None,:],dtype=torch.float32);c,h=planner.start(x);cur=torch.tensor([[g.stoi['<BOS>']]]);ids=[]
    for _ in range(4):
        log,h=planner.step(cur,c,h);i=int(log.argmax(-1));ids.append(i);cur=torch.tensor([[i]])
    log,h=planner.step(cur,c,h);eos=int(log.argmax(-1))==g.stoi['<EOS>'];a,err=g.seq_action(ids);return a,err,eos,[g.VOCAB[i] for i in ids]
# frozen 006E emitter
PAT=re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|-?\d+|[A-Za-z_<>]+|[{}\[\]:,]|[^\s]')
def toks(a):return PAT.findall(g.emit_json(a))
SPECIAL=['<PAD>','<BOS>','<EOS>'];ALL=[]
for k in g.KEYS:ALL.append(g.Action('READ',k));ALL.append(g.Action('CLEAR',k))
for a in g.KEYS:
    for b in g.KEYS:
        if a!=b:ALL.append(g.Action('READPAIR',a,b))
for k in g.KEYS:
    for v in g.VALS:ALL.append(g.Action('WRITE',k,value=v))
ALL.append(g.Action('DONE'))
cnt=Counter();[cnt.update(toks(a)) for a in ALL];EVOCAB=SPECIAL+sorted(cnt);estoi={t:i for i,t in enumerate(EVOCAB)}
KC2=[g.NONE]+g.KEYS;VC2=[-1]+g.VALS;TI={x:i for i,x in enumerate(g.TOOLS)};KI={x:i for i,x in enumerate(KC2)};VI={x:i for i,x in enumerate(VC2)}
def avec(a):
    x=np.zeros(5+9+9+11,np.float32)
    if a.tool in TI:x[TI[a.tool]]=1
    if a.k1 in KI:x[5+KI[a.k1]]=1
    if a.k2 in KI:x[14+KI[a.k2]]=1
    if a.value in VI:x[23+VI[a.value]]=1
    return x
class Emitter(nn.Module):
    def __init__(self,v):
        super().__init__();self.emb=nn.Embedding(v,24,padding_idx=0);self.ctx=nn.Sequential(nn.Linear(34,64),nn.ReLU());self.h0=nn.Linear(64,72);self.gru=nn.GRU(24+64,72,batch_first=True);self.out=nn.Linear(72,v)
    def start(self,x):c=self.ctx(x);return c,torch.tanh(self.h0(c)).unsqueeze(0)
    def step(self,t,c,h):z,h=self.gru(torch.cat([self.emb(t),c[:,None,:]],-1),h);return self.out(z[:,-1]),h
emz=torch.load('/mnt/data/006e_unpack/emitter.pt',map_location='cpu');emitter=Emitter(len(EVOCAB));emitter.load_state_dict(emz['state']);emitter.eval()
@torch.no_grad()
def emit(a,maxn=22):
    x=torch.tensor(avec(a)[None,:]);c,h=emitter.start(x);cur=torch.tensor([[estoi['<BOS>']]]);out=[]
    for _ in range(maxn):
        log,h=emitter.step(cur,c,h);i=int(log.argmax(-1));t=EVOCAB[i]
        if t=='<EOS>':break
        if t in ('<PAD>','<BOS>'):break
        out.append(t);cur=torch.tensor([[i]])
    return ''.join(out)
def valid_obj(o):
    if not isinstance(o,dict) or o.get('tool') not in g.TOOLS:return False
    t=o['tool']
    if t=='READ':return set(o)=={'tool','key'} and o.get('key') in g.KEYS
    if t=='READPAIR':return set(o)=={'tool','key1','key2'} and o.get('key1') in g.KEYS and o.get('key2') in g.KEYS and o['key1']!=o['key2']
    if t=='WRITE':return set(o)=={'tool','key','value'} and o.get('key') in g.KEYS and isinstance(o.get('value'),int) and o['value'] in g.VALS
    if t=='CLEAR':return set(o)=={'tool','key'} and o.get('key') in g.KEYS
    return set(o)=={'tool'}
def obj_action(o):
    t=o['tool']
    if t=='READPAIR':return g.Action(t,o['key1'],o['key2'])
    if t=='WRITE':return g.Action(t,o['key'],value=o['value'])
    if t in ('READ','CLEAR'):return g.Action(t,o['key'])
    return g.Action('DONE')

def run(t,cell,seed,styles,max_steps=14):
    rr=random.Random(seed);w=t.init.copy();lines=[t.request];ctr=0;oi=0;fd=0;perr=pschema=syntax=schema=emis=vf=0;had=False
    for step in range(max_steps):
        p,err,eos,ptok=plan(lines)
        if err:
            perr+=1;pschema+=int(err=='schema');lines.append('PLANNER_GENERATION_ERROR '+json.dumps({'error':err,'tokens':ptok},separators=(',',':')))
            if perr>=3:break
            continue
        txt=emit(p)
        try:o=json.loads(txt)
        except:syntax+=1;lines+=['ACTION_TEXT '+txt,'SYNTAX_ERROR'];continue
        if not valid_obj(o):schema+=1;lines+=['ACTION_TEXT '+txt,'SCHEMA_ERROR '+json.dumps({'error':'invalid_tool_arguments'},separators=(',',':'))];continue
        a=obj_action(o);emis+=int(a.tup()!=p.tup())
        if not fd and a.tup()!=t.oracle[min(oi,len(t.oracle)-1)].tup():fd=step+1
        oi+=1
        if a.tool in ('READ','READPAIR','WRITE','CLEAR'):ctr=g.append_exec(lines,w,a,ctr,rr,cell,seed+step,styles)
        else:
            lines.append('ACTION '+g.emit_json(a))
            if w==t.target:lines.append('VERIFY_OK');return {'ok':1,'steps':step+1,'first_div':fd,'planner_errors':perr,'planner_schema':pschema,'syntax_errors':syntax,'schema_errors':schema,'emitter_mismatch':emis,'verify_failures':vf,'trace':lines}
            vf+=1;had=True;diff={k:{'expected':t.target[k],'observed':w[k]} for k in g.KEYS if w[k]!=t.target[k]};lines+=['STATE '+json.dumps(w,separators=(',',':'),sort_keys=True),'VERIFY_FAIL '+json.dumps(diff,separators=(',',':'),sort_keys=True)]
            if vf>=2:break
    return {'ok':int(w==t.target),'steps':max_steps,'first_div':fd,'planner_errors':perr,'planner_schema':pschema,'syntax_errors':syntax,'schema_errors':schema,'emitter_mismatch':emis,'verify_failures':vf,'trace':lines}

pseed=[SEED_D+50000,SEED_D+60000,SEED_D+70000][PI-1];rr=random.Random(pseed);tasks=[g.make_task(rr) for _ in range(200)]
rows=[];traces=[]
for regime,styles in [('seen',g.SEEN_STYLES),('unseen',g.UNSEEN_STYLES)]:
    for cell in g.CELLS:
        for i,t in enumerate(tasks):
            r=run(t,cell,pseed+100000+i,styles);amb='multi_read' if any(a.tool=='READPAIR' for a in t.oracle) or sum(a.tool=='READ' for a in t.oracle)>1 else 'single_read'
            rows.append({'panel':PI,'task_id':i,'kind':t.kind,'ambiguity':amb,'schema_regime':regime,'condition':cell.name,'provenance':int(cell.provenance),'normalization':int(cell.normalization),'ok':r['ok'],'steps':r['steps'],'first_div':r['first_div'],'planner_errors':r['planner_errors'],'planner_schema':r['planner_schema'],'syntax_errors':r['syntax_errors'],'schema_errors':r['schema_errors'],'emitter_mismatch':r['emitter_mismatch'],'verify_failures':r['verify_failures']})
            if len(traces)<24 and (not r['ok']) and ((regime=='unseen' and not cell.normalization) or (regime=='seen' and cell.name=='P1_N0')):
                traces.append({'panel':PI,'task_id':i,'kind':t.kind,'regime':regime,'condition':cell.name,'request':t.request,'init':t.init,'target':t.target,'result':{k:r[k] for k in r if k!='trace'},'trace':r['trace']})
    print('DONE',PI,regime,flush=True)
with open(f'{OUT}/panel_{PI}_episodes.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
json.dump(traces,open(f'{OUT}/panel_{PI}_traces.json','w'),indent=2)
# compact panel summary
summary={}
for reg in ['seen','unseen']:
    summary[reg]={c.name:sum(r['ok'] for r in rows if r['schema_regime']==reg and r['condition']==c.name)/200 for c in g.CELLS}
json.dump(summary,open(f'{OUT}/panel_{PI}_summary.json','w'),indent=2);print(json.dumps(summary))
