import os,csv,json,glob,random,math,hashlib,shutil
from collections import defaultdict,Counter
import numpy as np
from scipy.stats import binomtest
OUT='/mnt/data/tool_chain_006g_evidence';SEED=26093041;SEED_D=26092821
files=sorted(glob.glob(OUT+'/panel_[123]_episodes.csv'))
rows=[]
for f in files:
    with open(f) as fh:rows.extend(list(csv.DictReader(fh)))
for r in rows:
    for k in ['panel','task_id','provenance','normalization','ok','steps','first_div','planner_errors','planner_schema','syntax_errors','schema_errors','emitter_mismatch','verify_failures']:
        r[k]=int(r[k])
# units indexed task/regime
by=defaultdict(dict)
for r in rows:by[(r['schema_regime'],r['panel'],r['task_id'])][r['condition']]=r
units=[]
for (reg,p,i),z in by.items():units.append({'schema_regime':reg,'panel':p,'task_id':i,'kind':z['P1_N1']['kind'],'ambiguity':z['P1_N1']['ambiguity'],**{c:z[c]['ok'] for c in ['P1_N1','P1_N0','P0_N1','P0_N0']}})
def factor(us):
    def m(k):return sum(u[k] for u in us)/len(us)
    a,b,c,d=[m(k) for k in ['P1_N1','P1_N0','P0_N1','P0_N0']]
    return {'P1_N1':a,'P1_N0':b,'P0_N1':c,'P0_N0':d,'provenance_main_pp':100*((a+b-c-d)/2),'normalization_main_pp':100*((a+c-b-d)/2),'interaction_pp':100*((a-c)-(b-d)),'normalized_provenance_pp':100*(a-c),'raw_provenance_pp':100*(b-d),'raw_mean':(b+d)/2,'normalized_mean':(a+c)/2}
def bootstrap(us,B=3000,seed=1):
    rr=random.Random(seed);n=len(us);vals=[]
    for _ in range(B):vals.append(factor([us[rr.randrange(n)] for __ in range(n)]))
    out={}
    for k in ['provenance_main_pp','normalization_main_pp','interaction_pp','normalized_provenance_pp','raw_provenance_pp','raw_mean','normalized_mean']:
        a=sorted(x[k] for x in vals);out[k]=[a[int(.025*B)],a[int(.975*B)]]
    return out
reg={}
for rg in ['seen','unseen']:
    u=[x for x in units if x['schema_regime']==rg];reg[rg]={'n':len(u),**factor(u),'bootstrap95':bootstrap(u,2500,SEED+(0 if rg=='seen' else 1)),'ambiguity':{},'task_family':{}}
    for amb in ['single_read','multi_read']:
        q=[x for x in u if x['ambiguity']==amb];reg[rg]['ambiguity'][amb]={'n':len(q),**factor(q),'bootstrap95':bootstrap(q,1500,SEED+(2 if amb=='single_read' else 3))}
    for kind in sorted(set(x['kind'] for x in u)):
        q=[x for x in u if x['kind']==kind];reg[rg]['task_family'][kind]={'n':len(q),**factor(q)}
# paired seen/unseen by same task
pairmap={(u['panel'],u['task_id'],u['schema_regime']):u for u in units};paired=[]
for p in [1,2,3]:
  for i in range(200):
    s=pairmap[(p,i,'seen')];u=pairmap[(p,i,'unseen')]
    paired.append({'panel':p,'task_id':i,'kind':s['kind'],'ambiguity':s['ambiguity'],'seen_norm_effect':((s['P1_N1']+s['P0_N1'])-(s['P1_N0']+s['P0_N0']))/2,'unseen_norm_effect':((u['P1_N1']+u['P0_N1'])-(u['P1_N0']+u['P0_N0']))/2,'raw_seen':(s['P1_N0']+s['P0_N0'])/2,'raw_unseen':(u['P1_N0']+u['P0_N0'])/2,'canonical_seen':(s['P1_N1']+s['P0_N1'])/2,'canonical_unseen':(u['P1_N1']+u['P0_N1'])/2})
diffs=[100*(x['unseen_norm_effect']-x['seen_norm_effect']) for x in paired]
rawdrop=[100*(x['raw_unseen']-x['raw_seen']) for x in paired]
canonchange=[100*(x['canonical_unseen']-x['canonical_seen']) for x in paired]
rr=random.Random(SEED+9);B=4000;bd=[];br=[];bc=[]
for _ in range(B):
    ss=[paired[rr.randrange(len(paired))] for __ in range(len(paired))];bd.append(100*np.mean([x['unseen_norm_effect']-x['seen_norm_effect'] for x in ss]));br.append(100*np.mean([x['raw_unseen']-x['raw_seen'] for x in ss]));bc.append(100*np.mean([x['canonical_unseen']-x['canonical_seen'] for x in ss]))
def ci(a):a=sorted(a);return [a[int(.025*len(a))],a[int(.975*len(a))]]
shift={'normalization_effect_increase_pp':float(np.mean(diffs)),'normalization_effect_increase_ci95':ci(bd),'raw_accuracy_change_pp':float(np.mean(rawdrop)),'raw_accuracy_change_ci95':ci(br),'canonical_accuracy_change_pp':float(np.mean(canonchange)),'canonical_accuracy_change_ci95':ci(bc)}
# paired sign exact tests for unseen normalized vs raw
sign={}
for prov,a,b in [('P1','P1_N1','P1_N0'),('P0','P0_N1','P0_N0')]:
    u=[x for x in units if x['schema_regime']=='unseen'];plus=sum(x[a]>x[b] for x in u);minus=sum(x[a]<x[b] for x in u);ties=len(u)-plus-minus;p=binomtest(plus,plus+minus,.5).pvalue if plus+minus else 1
    sign[prov]={'normalized_better':plus,'raw_better':minus,'ties':ties,'two_sided_sign_p':p}
# error and first-div summaries
errors={}
for rg in ['seen','unseen']:
    errors[rg]={}
    for c in ['P1_N1','P1_N0','P0_N1','P0_N0']:
        q=[r for r in rows if r['schema_regime']==rg and r['condition']==c];fails=[r for r in q if not r['ok']];fd=[r['first_div'] for r in fails if r['first_div']>0]
        errors[rg][c]={'n':len(q),'accuracy':sum(r['ok'] for r in q)/len(q),'planner_error_any':sum(r['planner_errors']>0 for r in q)/len(q),'planner_schema_any':sum(r['planner_schema']>0 for r in q)/len(q),'syntax_any':sum(r['syntax_errors']>0 for r in q)/len(q),'schema_any':sum(r['schema_errors']>0 for r in q)/len(q),'emitter_mismatch_any':sum(r['emitter_mismatch']>0 for r in q)/len(q),'mean_first_div_failure':float(np.mean(fd)) if fd else None,'median_first_div_failure':float(np.median(fd)) if fd else None}
# canonical per-task identical between regimes
canonical_agree={}
for c in ['P1_N1','P0_N1']:
    same=0
    for p in [1,2,3]:
      for i in range(200):
        same+=int(pairmap[(p,i,'seen')][c]==pairmap[(p,i,'unseen')][c])
    canonical_agree[c]=same/600
res={'experiment':'TOOL-CHAIN-GEOMETRY-006G','n_tasks':600,'n_trajectory_rows':len(rows),'schema_regimes':reg,'schema_shift_effect':shift,'unseen_normalization_sign_tests':sign,'error_first_divergence':errors,'canonical_task_outcome_agreement_seen_vs_unseen':canonical_agree,'pilot_gate':json.load(open(OUT+'/pilot_gate.json')),'data_geometry_precheck':json.load(open(OUT+'/data_geometry_precheck.json')),'diagnostics':json.load(open(OUT+'/diagnostics.json'))}
json.dump(res,open(OUT+'/results.json','w'),indent=2)
with open(OUT+'/episode_summary.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with open(OUT+'/paired_task_outcomes.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(units[0]));w.writeheader();w.writerows(units)
with open(OUT+'/schema_shift_paired.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(paired[0]));w.writeheader();w.writerows(paired)
# manifest
man={'experiment':'TOOL-CHAIN-GEOMETRY-006G','planner_sha256':hashlib.sha256(open(OUT+'/planner.pt','rb').read()).hexdigest(),'train_script_sha256':hashlib.sha256(open('/mnt/data/tool_chain_006g_train.py','rb').read()).hexdigest(),'formal_script_sha256':hashlib.sha256(open('/mnt/data/tool_chain_006g_formal_panel.py','rb').read()).hexdigest(),'seen_raw_styles':[0,1,2],'unseen_raw_styles':[3,4,5],'formal_task_seeds':[SEED_D+50000,SEED_D+60000,SEED_D+70000],'note':'Planner trained only on raw styles 0-2. Raw styles 3-5 occupied reserved feature coordinates that were never active during training. Canonical normalization maps all styles to the same trained value channels.'}
json.dump(man,open(OUT+'/source_manifest.json','w'),indent=2)
for s in ['/mnt/data/tool_chain_006g_train.py','/mnt/data/tool_chain_006g_gate.py','/mnt/data/tool_chain_006g_geometry.py','/mnt/data/tool_chain_006g_formal_panel.py','/mnt/data/tool_chain_006g_diagnostics.py','/mnt/data/tool_chain_006g_aggregate.py']:
    if os.path.exists(s):shutil.copy2(s,OUT+'/'+os.path.basename(s))
print(json.dumps({'seen':reg['seen'],'unseen':reg['unseen'],'shift':shift,'sign':sign,'canonical_agree':canonical_agree}))
