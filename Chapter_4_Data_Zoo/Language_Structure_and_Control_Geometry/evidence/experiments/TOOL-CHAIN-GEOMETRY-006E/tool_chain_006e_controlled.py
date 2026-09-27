import os,json,random,re,hashlib,pickle,csv,shutil,zipfile
from collections import defaultdict,Counter
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
OUT='/mnt/data/tool_chain_006e_final_evidence';os.makedirs(OUT,exist_ok=True)
SEED=26092791;random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))
SRC='/mnt/data/tool_chain_006d_final_evidence/tool_chain_006d_final_eval.py';source=open(SRC).read();prefix=source.split("OUT='/mnt/data/tool_chain_006d_final_evidence'")[0];ns={};exec(prefix,ns)
Action=ns['Action'];CELLS=ns['CELLS'];KEYS=ns['KEYS'];VALS=ns['VALS'];TOOLS=ns['TOOLS'];NONE=ns['NONE'];KINDS=ns['KINDS'];D=ns['D'];make_task=ns['make_task'];features=ns['features'];append_exec=ns['append_exec'];emit_json=ns['emit_json']
# frozen 006D planner
pk=pickle.load(open('/mnt/data/tool_chain_006d_final_evidence/policy.pkl','rb'));models=pk['models'];KC=pk['KC'];VC=pk['VC']
def planner(lines):
 x=features(lines).reshape(1,-1);ix=[int(m.predict(x)[0]) for m in models];return Action(TOOLS[ix[0]],KC[ix[1]],KC[ix[2]],VC[ix[3]])
# tokenizer/output vocab
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
cnt=Counter();[cnt.update(toks(a)) for a in ALL];vocab=SPECIAL+sorted(cnt);stoi={t:i for i,t in enumerate(vocab)}
KC2=[NONE]+KEYS;VC2=[-1]+VALS;TI={x:i for i,x in enumerate(TOOLS)};KI={x:i for i,x in enumerate(KC2)};VI={x:i for i,x in enumerate(VC2)}
def avec(a):
 x=np.zeros(5+9+9+11,np.float32);x[TI[a.tool]]=1;x[5+KI[a.k1]]=1;x[14+KI[a.k2]]=1;x[23+VI[a.value]]=1;return x
YS=[];XS=[]
for a in ALL:
 q=[stoi['<BOS>']]+[stoi[x] for x in toks(a)]+[stoi['<EOS>']];XS.append(avec(a));YS.append(q)
class Emitter(nn.Module):
 def __init__(self,v):
  super().__init__();self.emb=nn.Embedding(v,24,padding_idx=0);self.ctx=nn.Sequential(nn.Linear(34,64),nn.ReLU());self.h0=nn.Linear(64,72);self.gru=nn.GRU(24+64,72,batch_first=True);self.out=nn.Linear(72,v)
 def forward(self,x,t):
  c=self.ctx(x);h=torch.tanh(self.h0(c)).unsqueeze(0);e=self.emb(t);z,_=self.gru(torch.cat([e,c[:,None,:].expand(-1,e.size(1),-1)],-1),h);return self.out(z)
 def start(self,x):c=self.ctx(x);return c,torch.tanh(self.h0(c)).unsqueeze(0)
 def step(self,t,c,h):z,h=self.gru(torch.cat([self.emb(t),c[:,None,:]],-1),h);return self.out(z[:,-1]),h
# load already-trained unconstrained emitter
z_em=torch.load(OUT+'/emitter.pt',map_location='cpu')
m=Emitter(len(vocab));m.load_state_dict(z_em['state']);m.eval();hist=z_em.get('history',[])
@torch.no_grad()
def gen(a,maxn=22):
 x=torch.tensor(avec(a)[None,:]);c,h=m.start(x);cur=torch.tensor([[stoi['<BOS>']]]);out=[]
 for _ in range(maxn):
  log,h=m.step(cur,c,h);i=int(log.argmax(-1));t=vocab[i]
  if t=='<EOS>':break
  if t in ('<PAD>','<BOS>'):break
  out.append(t);cur=torch.tensor([[i]])
 return ''.join(out)
def valid(o):
 if not isinstance(o,dict) or o.get('tool') not in TOOLS:return False
 t=o['tool']
 if t=='READ':return set(o)=={'tool','key'} and o.get('key') in KEYS
 if t=='READPAIR':return set(o)=={'tool','key1','key2'} and o.get('key1') in KEYS and o.get('key2') in KEYS and o['key1']!=o['key2']
 if t=='WRITE':return set(o)=={'tool','key','value'} and o.get('key') in KEYS and isinstance(o.get('value'),int) and o['value'] in VALS
 if t=='CLEAR':return set(o)=={'tool','key'} and o.get('key') in KEYS
 return set(o)=={'tool'}
def to_a(o):
 t=o['tool']
 if t=='READPAIR':return Action(t,o['key1'],o['key2'])
 if t=='WRITE':return Action(t,o['key'],value=o['value'])
 if t in ('READ','CLEAR'):return Action(t,o['key'])
 return Action('DONE')
# emitter assay
ass=[]
for a in ALL:
 s=gen(a)
 try:o=json.loads(s);jp=1;sv=int(valid(o));b=to_a(o) if sv else None
 except:o=None;jp=0;sv=0;b=None
 ass.append({'plan':emit_json(a),'generated':s,'json_parse':jp,'schema_valid':sv,'semantic_exact':int(b is not None and b.tup()==a.tup())})
emit_stats={k:sum(r[k] for r in ass)/len(ass) for k in ['json_parse','schema_valid','semantic_exact']};emit_stats['n_actions']=len(ass)
print('EMITTER',emit_stats,flush=True)
# save emitter before formal run
torch.save({'state':m.state_dict(),'vocab':vocab,'history':hist,'seed':SEED},OUT+'/emitter.pt')
with open(OUT+'/emitter_action_assay.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(ass[0]));w.writeheader();w.writerows(ass)

def run(t,cell,seed,max_steps=14):
 rr=random.Random(seed);w=t.init.copy();lines=[t.request];ctr=0;oi=0;fd=0;syn=sch=emit_mismatch=vf=0;recovered=0;genlog=[]
 for step in range(max_steps):
  p=planner(lines);txt=gen(p);genlog.append({'planned':emit_json(p),'generated':txt})
  try:o=json.loads(txt)
  except:
   syn+=1;lines+=['ACTION_TEXT '+txt,'SYNTAX_ERROR'];continue
  if not valid(o):
   sch+=1;lines+=['ACTION_TEXT '+txt,'SCHEMA_ERROR '+json.dumps({'error':'invalid_tool_arguments'},separators=(',',':'))];continue
  a=to_a(o);emit_mismatch+=int(a.tup()!=p.tup())
  if not fd and a.tup()!=t.oracle[min(oi,len(t.oracle)-1)].tup():fd=step+1
  oi+=1
  if a.tool in ('READ','READPAIR','WRITE','CLEAR'):ctr=append_exec(lines,w,a,ctr,rr,cell,seed+step)
  else:
   lines.append('ACTION '+emit_json(a))
   if w==t.target:
    lines.append('VERIFY_OK');return {'ok':1,'steps':step+1,'first_div':fd,'syntax_errors':syn,'schema_errors':sch,'emitter_mismatch':emit_mismatch,'verify_failures':vf,'recovered':recovered,'trace':lines,'genlog':genlog}
   vf+=1;diff={k:{'expected':t.target[k],'observed':w[k]} for k in KEYS if w[k]!=t.target[k]};lines+=['STATE '+json.dumps(w,separators=(',',':'),sort_keys=True),'VERIFY_FAIL '+json.dumps(diff,separators=(',',':'),sort_keys=True)]
   if vf>=2:break
 return {'ok':int(w==t.target),'steps':max_steps,'first_div':fd,'syntax_errors':syn,'schema_errors':sch,'emitter_mismatch':emit_mismatch,'verify_failures':vf,'recovered':int(vf and w==t.target),'trace':lines,'genlog':genlog}
# exact same heldout panels as 006D
allrows=[];traces=[];task_cache={}
SEED_D=26092821
for pi,pseed in enumerate([SEED_D+50000,SEED_D+60000,SEED_D+70000],1):
 rr=random.Random(pseed);tasks=[make_task(rr) for _ in range(200)];task_cache[pi]=tasks
 for cell in CELLS:
  for i,t in enumerate(tasks):
   r=run(t,cell,pseed+100000+i);amb='multi_read' if any(a.tool=='READPAIR' for a in t.oracle) or sum(a.tool=='READ' for a in t.oracle)>1 else 'single_read'
   allrows.append({'panel':pi,'task_id':i,'kind':t.kind,'ambiguity':amb,'condition':cell.name,'provenance':int(cell.provenance),'normalization':int(cell.normalization),'ok':r['ok'],'steps':r['steps'],'first_div':r['first_div'],'syntax_errors':r['syntax_errors'],'schema_errors':r['schema_errors'],'emitter_mismatch':r['emitter_mismatch'],'verify_failures':r['verify_failures'],'recovered':r['recovered']})
   if len(traces)<20 and ((not r['ok'] and cell.name=='P1_N1') or r['syntax_errors'] or r['schema_errors'] or r['emitter_mismatch']):traces.append({'panel':pi,'task_id':i,'kind':t.kind,'cell':cell.name,'request':t.request,'init':t.init,'target':t.target,'trace':r['trace'],'generation':r['genlog']})
 print('PANEL',pi,'done',flush=True)
# factorial summaries
def factor(units):
 def mean(k):return sum(u[k] for u in units)/len(units)
 a,b,c,d=map(mean,['P1_N1','P1_N0','P0_N1','P0_N0']);return {'P1_N1':a,'P1_N0':b,'P0_N1':c,'P0_N0':d,'provenance_main_pp':100*((a+b-c-d)/2),'normalization_main_pp':100*((a+c-b-d)/2),'interaction_pp':100*((a-c)-(b-d))}
by=defaultdict(dict)
for r in allrows:by[(r['panel'],r['task_id'])][r['condition']]=r
units=[]
for (p,i),z in by.items():units.append({'panel':p,'task_id':i,'kind':z['P1_N1']['kind'],'ambiguity':z['P1_N1']['ambiguity'],**{c.name:z[c.name]['ok'] for c in CELLS}})
def boot(uu,B=2000):
 rr=random.Random(SEED+99);vals=[]
 for _ in range(B):vals.append(factor([uu[rr.randrange(len(uu))] for __ in uu]))
 out={}
 for k in ['provenance_main_pp','normalization_main_pp','interaction_pp']:
  a=sorted(x[k] for x in vals);out[k]=[a[int(.025*B)],a[int(.975*B)]]
 return out
pooled=factor(units);sub={}
for amb in ['single_read','multi_read']:
 u=[x for x in units if x['ambiguity']==amb];sub[amb]={'n':len(u),**factor(u),'bootstrap95':boot(u,1200)}
# compare exact episode outcomes with 006D
old={}
with open('/mnt/data/tool_chain_006d_final_evidence/episode_summary.csv') as f:
 for r in csv.DictReader(f):old[(int(r['panel']),int(r['task_id']),r['condition'])]=int(r['ok'])
agree=sum(int(old[(r['panel'],r['task_id'],r['condition'])]==r['ok']) for r in allrows)/len(allrows);delta=sum(r['ok']-old[(r['panel'],r['task_id'],r['condition'])] for r in allrows)/len(allrows)
cell={}
for c in [x.name for x in CELLS]:
 q=[r for r in allrows if r['condition']==c];cell[c]={'acc':sum(r['ok'] for r in q)/len(q),'syntax_any':sum(r['syntax_errors']>0 for r in q)/len(q),'schema_any':sum(r['schema_errors']>0 for r in q)/len(q),'emitter_mismatch_any':sum(r['emitter_mismatch']>0 for r in q)/len(q)}
res={'experiment':'TOOL-CHAIN-GEOMETRY-006E','design':'frozen 006D planner with unconstrained neural autoregressive JSON action emitter','seed':SEED,'test_panels':'exact same 3 x 200 held-out panels as final 006D','emitter_assay':emit_stats,'conditions':cell,'pooled':pooled,'bootstrap95':boot(units,2500),'ambiguity_subgroups':sub,'paired_outcome_agreement_with_006D':agree,'mean_accuracy_delta_vs_006D':delta,'pilot_diagnostics':{'end_to_end_AR_v1':{'oracle_action_exact':0.22181818181818183,'json_parse':1.0,'schema_valid':1.0,'final_state_all_cells':0.006666666666666667},'semantic_weighted_GRU_epoch1':{'oracle_action_exact':0.19152854511970535,'json_parse':0.5359116022099447,'schema_valid':0.35359116022099446}}}
json.dump(res,open(OUT+'/results.json','w'),indent=2);json.dump(traces,open(OUT+'/representative_traces.json','w'),indent=2)
with open(OUT+'/episode_summary.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
with open(OUT+'/paired_task_outcomes.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(units[0]));w.writeheader();w.writerows(units)
# figures
labels=['P1_N1','P1_N0','P0_N1','P0_N0'];oldres=json.load(open('/mnt/data/tool_chain_006d_final_evidence/results.json'))['pooled']
fig=plt.figure(figsize=(8,4.6));ax=fig.add_subplot(111);x=np.arange(4);w=.36;ax.bar(x-w/2,[100*oldres[k] for k in labels],w,label='006D structured action');ax.bar(x+w/2,[100*pooled[k] for k in labels],w,label='006E generated JSON');ax.set_xticks(x,labels);ax.set_ylabel('Final-state accuracy (%)');ax.set_title('Figure 4.21. Structured vs autoregressive JSON action surface');ax.legend();fig.tight_layout();fig.savefig(OUT+'/Figure_4_21_structured_vs_generated.png',dpi=180);plt.close(fig)
fig=plt.figure(figsize=(7.5,4.6));ax=fig.add_subplot(111);labs=['single_read','multi_read'];xx=np.arange(2);ax.bar(xx-.18,[sub[k]['interaction_pp'] for k in labs],.36,label='006E interaction');oldsub=json.load(open('/mnt/data/tool_chain_006d_final_evidence/results.json'))['ambiguity_subgroups'];ax.bar(xx+.18,[oldsub[k]['interaction_pp'] for k in labs],.36,label='006D interaction');ax.axhline(0,linewidth=.8);ax.set_xticks(xx,['Single read','Multi read']);ax.set_ylabel('P × N interaction (pp)');ax.set_title('Figure 4.22. Interaction survives generated action serialization');ax.legend();fig.tight_layout();fig.savefig(OUT+'/Figure_4_22_interaction_transfer.png',dpi=180);plt.close(fig)
fig=plt.figure(figsize=(8,4.6));ax=fig.add_subplot(111);metrics=['syntax_any','schema_any','emitter_mismatch_any'];xx=np.arange(4);bw=.22
for j,met in enumerate(metrics):ax.bar(xx+(j-1)*bw,[100*cell[c][met] for c in labels],bw,label=met.replace('_',' '))
ax.set_xticks(xx,labels);ax.set_ylabel('Trajectories with error (%)');ax.set_title('Figure 4.23. Text-surface error channels under greedy decoding');ax.legend();fig.tight_layout();fig.savefig(OUT+'/Figure_4_23_generation_errors.png',dpi=180);plt.close(fig)
# manifest/package
shutil.copy2(__file__,OUT+'/tool_chain_006e_controlled.py');shutil.copy2(SRC,OUT+'/006d_reader_reference.py')
man={'seed':SEED,'planner_sha256':hashlib.sha256(open('/mnt/data/tool_chain_006d_final_evidence/policy.pkl','rb').read()).hexdigest(),'emitter_sha256':hashlib.sha256(open(OUT+'/emitter.pt','rb').read()).hexdigest(),'script_sha256':hashlib.sha256(open(__file__,'rb').read()).hexdigest(),'formal_trajectories':len(allrows),'same_006D_panels':True,'note':'Planner and event reader are frozen from final 006D. Only structured action serialization is replaced by unconstrained token-autoregressive neural JSON emission.'};json.dump(man,open(OUT+'/source_manifest.json','w'),indent=2)
print('FINAL',json.dumps(res),flush=True)
