import os,json,random,re,hashlib,csv,shutil,importlib.util
from collections import defaultdict,Counter
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

OUT='/mnt/data/tool_chain_006f_evidence';os.makedirs(OUT,exist_ok=True)
SEED=26092931;SEED_D=26092821
random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))
# planner module and exact 006D world
spec=importlib.util.spec_from_file_location('tp','/mnt/data/tool_chain_006f_train_pilot.py');tp=importlib.util.module_from_spec(spec);spec.loader.exec_module(tp)
Action=tp.Action;CELLS=tp.CELLS;KEYS=tp.KEYS;VALS=tp.VALS;TOOLS=tp.TOOLS;NONE=tp.NONE;make_task=tp.make_task;features=tp.features;append_exec=tp.append_exec;emit_json=tp.emit_json
pz=torch.load(OUT+'/planner.pt',map_location='cpu');planner=tp.GenPlanner(pz['D'],len(pz['vocab']),pz['emb'],pz['ctx'],pz['hid']);planner.load_state_dict(pz['state']);planner.eval()
VOCAB=tp.VOCAB;stoi=tp.stoi;seq_action=tp.seq_action
@torch.no_grad()
def plan(lines):
    x=torch.tensor(features(lines)[None,:],dtype=torch.float32);c,h=planner.start(x);cur=torch.tensor([[stoi['<BOS>']]]);ids=[]
    for _ in range(4):
        log,h=planner.step(cur,c,h);i=int(log.argmax(-1));ids.append(i);cur=torch.tensor([[i]])
    log,h=planner.step(cur,c,h);eos=int(log.argmax(-1))==stoi['<EOS>'];a,err=seq_action(ids);return a,err,eos,[VOCAB[i] for i in ids]
# 006E neural JSON emitter, held fixed
PAT=re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|-?\d+|[A-Za-z_<>]+|[{}\[\]:,]|[^\s]')
def toks(a):return PAT.findall(emit_json(a))
SPECIAL=['<PAD>','<BOS>','<EOS>']
ALL=[]
for k in KEYS:ALL.append(Action('READ',k));ALL.append(Action('CLEAR',k))
for a in KEYS:
 for b in KEYS:
  if a!=b:ALL.append(Action('READPAIR',a,b))
for k in KEYS:
 for v in VALS:ALL.append(Action('WRITE',k,value=v))
ALL.append(Action('DONE'))
cnt=Counter();[cnt.update(toks(a)) for a in ALL];EVOCAB=SPECIAL+sorted(cnt);estoi={t:i for i,t in enumerate(EVOCAB)}
KC2=[NONE]+KEYS;VC2=[-1]+VALS;TI={x:i for i,x in enumerate(TOOLS)};KI={x:i for i,x in enumerate(KC2)};VI={x:i for i,x in enumerate(VC2)}
def avec(a):
 x=np.zeros(5+9+9+11,np.float32);x[TI[a.tool]]=1;x[5+KI[a.k1]]=1;x[14+KI[a.k2]]=1;x[23+VI[a.value]]=1;return x
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
 if not isinstance(o,dict) or o.get('tool') not in TOOLS:return False
 t=o['tool']
 if t=='READ':return set(o)=={'tool','key'} and o.get('key') in KEYS
 if t=='READPAIR':return set(o)=={'tool','key1','key2'} and o.get('key1') in KEYS and o.get('key2') in KEYS and o['key1']!=o['key2']
 if t=='WRITE':return set(o)=={'tool','key','value'} and o.get('key') in KEYS and isinstance(o.get('value'),int) and o['value'] in VALS
 if t=='CLEAR':return set(o)=={'tool','key'} and o.get('key') in KEYS
 return set(o)=={'tool'}
def obj_action(o):
 t=o['tool']
 if t=='READPAIR':return Action(t,o['key1'],o['key2'])
 if t=='WRITE':return Action(t,o['key'],value=o['value'])
 if t in ('READ','CLEAR'):return Action(t,o['key'])
 return Action('DONE')
# exhaustive legal emitter gate
ass=[]
for a in ALL:
 txt=emit(a)
 try:o=json.loads(txt);jp=1;sv=int(valid_obj(o));b=obj_action(o) if sv else None
 except:o=None;jp=0;sv=0;b=None
 ass.append({'plan':emit_json(a),'generated':txt,'json_parse':jp,'schema_valid':sv,'semantic_exact':int(b is not None and b.tup()==a.tup())})
emit_stats={k:sum(r[k] for r in ass)/len(ass) for k in ['json_parse','schema_valid','semantic_exact']};emit_stats['n_actions']=len(ass)
EMIT_CACHE={r['plan']:r['generated'] for r in ass}
print('EMITTER',emit_stats,flush=True)

def run(t,cell,seed,max_steps=14):
 rr=random.Random(seed);w=t.init.copy();lines=[t.request];ctr=0;oi=0;fd=0;planner_err=planner_schema=0;syntax=schema=0;em_mis=0;vf=0;recovered=0;had_fail=False;genlog=[]
 for step in range(max_steps):
  p,perr,eos,ptok=plan(lines)
  if perr:
   planner_err+=1;planner_schema+=int(perr=='schema');lines.append('PLANNER_GENERATION_ERROR '+json.dumps({'error':perr,'tokens':ptok},separators=(',',':')))
   if planner_err>=3:break
   continue
  ptxt=emit_json(p);txt=EMIT_CACHE[ptxt];genlog.append({'planner_tokens':ptok,'planned':ptxt,'generated':txt})
  try:o=json.loads(txt)
  except:
   syntax+=1;lines+=['ACTION_TEXT '+txt,'SYNTAX_ERROR'];continue
  if not valid_obj(o):
   schema+=1;lines+=['ACTION_TEXT '+txt,'SCHEMA_ERROR '+json.dumps({'error':'invalid_tool_arguments'},separators=(',',':'))];continue
  a=obj_action(o);em_mis+=int(a.tup()!=p.tup())
  if not fd and a.tup()!=t.oracle[min(oi,len(t.oracle)-1)].tup():fd=step+1
  oi+=1
  if a.tool in ('READ','READPAIR','WRITE','CLEAR'):
   ctr=append_exec(lines,w,a,ctr,rr,cell,seed+step)
  else:
   lines.append('ACTION '+emit_json(a))
   if w==t.target:
    recovered=int(had_fail);lines.append('VERIFY_OK');return {'ok':1,'steps':step+1,'first_div':fd,'planner_errors':planner_err,'planner_schema_errors':planner_schema,'syntax_errors':syntax,'schema_errors':schema,'emitter_mismatch':em_mis,'verify_failures':vf,'recovered':recovered,'trace':lines,'genlog':genlog}
   vf+=1;had_fail=True;diff={k:{'expected':t.target[k],'observed':w[k]} for k in KEYS if w[k]!=t.target[k]};lines+=['STATE '+json.dumps(w,separators=(',',':'),sort_keys=True),'VERIFY_FAIL '+json.dumps(diff,separators=(',',':'),sort_keys=True)]
   if vf>=2:break
 return {'ok':int(w==t.target),'steps':max_steps,'first_div':fd,'planner_errors':planner_err,'planner_schema_errors':planner_schema,'syntax_errors':syntax,'schema_errors':schema,'emitter_mismatch':em_mis,'verify_failures':vf,'recovered':int(had_fail and w==t.target),'trace':lines,'genlog':genlog}

def factor(units):
 def mean(k):return sum(u[k] for u in units)/len(units)
 a,b,c,d=map(mean,['P1_N1','P1_N0','P0_N1','P0_N0'])
 return {'P1_N1':a,'P1_N0':b,'P0_N1':c,'P0_N0':d,'provenance_main_pp':100*((a+b-c-d)/2),'normalization_main_pp':100*((a+c-b-d)/2),'interaction_pp':100*((a-c)-(b-d))}
def boot(uu,B=2000):
 rr=random.Random(SEED+99);vals=[];n=len(uu)
 for _ in range(B):vals.append(factor([uu[rr.randrange(n)] for __ in range(n)]))
 out={}
 for k in ['provenance_main_pp','normalization_main_pp','interaction_pp']:
  a=sorted(x[k] for x in vals);out[k]=[a[int(.025*B)],a[int(.975*B)]]
 return out

rows=[];traces=[];task_cache={}
for pi,pseed in enumerate([SEED_D+50000,SEED_D+60000,SEED_D+70000],1):
 rr=random.Random(pseed);tasks=[make_task(rr) for _ in range(200)];task_cache[pi]=tasks
 for cell in CELLS:
  for i,t in enumerate(tasks):
   r=run(t,cell,pseed+100000+i);amb='multi_read' if any(a.tool=='READPAIR' for a in t.oracle) or sum(a.tool=='READ' for a in t.oracle)>1 else 'single_read'
   rows.append({'panel':pi,'task_id':i,'kind':t.kind,'ambiguity':amb,'condition':cell.name,'provenance':int(cell.provenance),'normalization':int(cell.normalization),'ok':r['ok'],'steps':r['steps'],'first_div':r['first_div'],'planner_errors':r['planner_errors'],'planner_schema_errors':r['planner_schema_errors'],'syntax_errors':r['syntax_errors'],'schema_errors':r['schema_errors'],'emitter_mismatch':r['emitter_mismatch'],'verify_failures':r['verify_failures'],'recovered':r['recovered']})
   if len(traces)<36 and ((not r['ok'] and cell.name=='P1_N1') or r['planner_errors'] or r['syntax_errors'] or r['schema_errors'] or (r['first_div'] and r['first_div']>=3 and not r['ok'])):
    traces.append({'panel':pi,'task_id':i,'kind':t.kind,'cell':cell.name,'request':t.request,'init':t.init,'target':t.target,'result':{k:r[k] for k in ['ok','steps','first_div','planner_errors','planner_schema_errors','syntax_errors','schema_errors','emitter_mismatch','verify_failures','recovered']},'trace':r['trace'],'generation':r['genlog']})

 # checkpoint rows after every completed panel
 with open(OUT+'/episode_summary.partial.csv','w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 json.dump(traces,open(OUT+'/representative_traces.partial.json','w'),indent=2)
 print('PANEL',pi,'done',flush=True)
by=defaultdict(dict)
for r in rows:by[(r['panel'],r['task_id'])][r['condition']]=r
units=[]
for (p,i),z in by.items():units.append({'panel':p,'task_id':i,'kind':z['P1_N1']['kind'],'ambiguity':z['P1_N1']['ambiguity'],**{c.name:z[c.name]['ok'] for c in CELLS}})
pooled=factor(units);ci=boot(units,2500);sub={}
for amb in ['single_read','multi_read']:
 u=[x for x in units if x['ambiguity']==amb];sub[amb]={'n':len(u),**factor(u),'bootstrap95':boot(u,1500)}
panels={}
for p in [1,2,3]:panels[str(p)]={c.name:sum(r['ok'] for r in rows if r['panel']==p and r['condition']==c.name)/200 for c in CELLS}
cell={}
for c in CELLS:
 q=[r for r in rows if r['condition']==c.name]
 cell[c.name]={'acc':sum(r['ok'] for r in q)/len(q),'planner_error_any':sum(r['planner_errors']>0 for r in q)/len(q),'planner_schema_any':sum(r['planner_schema_errors']>0 for r in q)/len(q),'syntax_any':sum(r['syntax_errors']>0 for r in q)/len(q),'schema_any':sum(r['schema_errors']>0 for r in q)/len(q),'emitter_mismatch_any':sum(r['emitter_mismatch']>0 for r in q)/len(q),'recovery_rate':sum(r['recovered'] for r in q)/len(q)}
# compare exact same task outcomes vs 006D and 006E
comparisons={}
for label,path in [('006D','/mnt/data/006d_unpack/tool_chain_006d_final_evidence/episode_summary.csv'),('006E','/mnt/data/006e_unpack/episode_summary.csv')]:
 old={}
 with open(path) as f:
  for r in csv.DictReader(f):old[(int(r['panel']),int(r['task_id']),r['condition'])]=int(r['ok'])
 agree=sum(int(old[(r['panel'],r['task_id'],r['condition'])]==r['ok']) for r in rows)/len(rows);delta=sum(r['ok']-old[(r['panel'],r['task_id'],r['condition'])] for r in rows)/len(rows)
 comparisons[label]={'paired_outcome_agreement':agree,'mean_accuracy_delta':delta}
prefix_stats=json.load(open(OUT+'/pilot_gate.json'))['prefix_pilot']
res={'experiment':'TOOL-CHAIN-GEOMETRY-006F','design':'end-to-end generative action path: autoregressive semantic planner -> frozen 006E autoregressive JSON emitter -> schema validator -> executor','seed':SEED,'training_checkpoint_epochs':len(pz['history']),'training_nll':pz['history'],'pilot_gate':json.load(open(OUT+'/pilot_gate.json')),'emitter_assay':emit_stats,'formal_prefix_competence':prefix_stats,'n_tasks':600,'n_trajectories':len(rows),'conditions':cell,'panels':panels,'pooled':pooled,'bootstrap95':ci,'ambiguity_subgroups':sub,'paired_comparison':comparisons}
json.dump(res,open(OUT+'/results.json','w'),indent=2);json.dump(traces,open(OUT+'/representative_traces.json','w'),indent=2)
with open(OUT+'/episode_summary.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with open(OUT+'/paired_task_outcomes.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(units[0]));w.writeheader();w.writerows(units)
with open(OUT+'/emitter_action_assay.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(ass[0]));w.writeheader();w.writerows(ass)
# manifests
man={'experiment':'TOOL-CHAIN-GEOMETRY-006F','planner_sha256':hashlib.sha256(open(OUT+'/planner.pt','rb').read()).hexdigest(),'emitter_sha256':hashlib.sha256(open('/mnt/data/006e_unpack/emitter.pt','rb').read()).hexdigest(),'script_sha256':hashlib.sha256(open(__file__,'rb').read()).hexdigest(),'reader_reference_sha256':hashlib.sha256(open(SRC,'rb').read()).hexdigest(),'formal_rows':len(rows),'formal_task_seeds':[SEED_D+50000,SEED_D+60000,SEED_D+70000],'note':'Formal run uses exact same held-out task panels and 2x2 interface cells as final 006D. Generative planner checkpoint first passed independent competence gate before factorial execution.'}
json.dump(man,open(OUT+'/source_manifest.json','w'),indent=2);shutil.copy2(__file__,OUT+'/tool_chain_006f_formal.py');shutil.copy2(SRC,OUT+'/006d_reader_reference.py')
print('RESULT',json.dumps(res),flush=True)
