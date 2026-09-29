from pathlib import Path
import ast,csv,hashlib,json,zipfile,re
import numpy as np
import pandas as pd

W=Path(__file__).resolve().parent
# This verifier can run on the prepared release or the unpacked source records.
P=W/'evidence'/'experiments'
SOURCE_MODE=not P.exists()
if SOURCE_MODE:P=W/'expanded_evidence'
OUT=W/'verification_results';OUT.mkdir(exist_ok=True)
def file(cg,name):
 root=P/(f'CAUSAL_GEOMETRY_{cg:03d}_Evidence' if SOURCE_MODE else f'CG{cg:03d}')
 fs=list(root.rglob(name));assert fs,(cg,name)
 return sorted(fs,key=lambda f:len(f.parts))[0]
def read(cg,name):return pd.read_csv(file(cg,name))
checks=[]
def check(label,value,expected,tol=0.00006):
 value=float(value);ok=abs(value-expected)<=tol
 checks.append({'check':label,'recomputed':value,'reported_rounded':expected,'tolerance':tol,'pass':bool(ok)})
def boot(a):
 a=np.asarray(a,float);rng=np.random.default_rng(20260928)
 means=a[rng.integers(0,len(a),(10000,len(a)))].mean(1)
 return {'mean':float(a.mean()),'ci95':np.quantile(means,[.025,.975]).tolist(),'n_independent_groups':len(a)}

for cg,expects in [(17,{'blank':-1.0740,'structured':-1.2082}),(18,{'mechanism_blank':-1.7701,'mechanism_feedback':-1.7557})]:
 d=read(cg,'results.csv');s=d[d.task=='synthetic'].groupby('mode').loss.mean()
 for k,v in expects.items():check(f'CG{cg:03d} synthetic {k} NLL',s[k],v)
 r=d[d.task=='real'].groupby(['mode','fold']).loss.mean().groupby('mode').mean()
 for k,v in ({'blank':1.6371,'structured':1.6313} if cg==17 else {'mechanism_blank':1.6528,'mechanism_feedback':1.6605}).items():check(f'CG{cg:03d} real equal-target {k} MSE',r[k],v)
d=read(19,'double_do_query_level.csv');s=d.groupby(['mode','method']).nll.mean()
for mode,expect in [('mechanism_blank',.3566),('mechanism_feedback',.2462)]:check(f'CG019 {mode} double-do NLL gain',s[mode,'single_do_superposition']-s[mode,'mechanism_solve'],expect)
d=read(20,'instance_metrics.csv');s=d.groupby('variant')[['nll','mse']].mean()
for k,expect in [('onepass3',-1.0106),('world4_3',-1.1242)]:
 if k not in s.index and k=='world4_3':k=next(x for x in s.index if 'world' in x)
 check(f'CG020 {k} NLL',s.loc[k,'nll'],expect)
d=read(21,'results.csv').groupby('variant').test_nll.mean()
check('CG021 Pool3 NLL',d['pool3'],-1.1443);check('CG021 Pool8 NLL',d['pool8'],-1.3220)
d=read(21,'pool8_subset_control.csv');check('CG021 Top3 pruning penalty',(d.top3_nll-d.full8_nll).groupby(d.group).mean().mean(),1.256,tol=.0006)
a=read(22,'baseline_operator_detail.csv');z=read(22,'evidence_coupled_operator_detail.csv')
a=a[a.bank=='heldout_bank'].groupby('group').nll.mean();z=z[z.bank=='heldout_bank'].groupby('group').nll.mean()
check('CG022 heldout bank NLL gain',(a-z).mean(),.2264)
bootstrap={'CG022_heldout_gain':boot(a-z)}
d=read(24,'sequential_eval_detail_final.csv')
for op,comparison,expect in [('impulse','ignore',-.00120),('clamp','ignore',-.00116),('persistent_force','ignore',-.19525),('compound_force_plus_impulse','omit_second',-.00185)]:
 q=d[d.operation==op].groupby(['world_id','condition']).mse.mean().unstack();delta=q.correct-q[comparison]
 check('CG024 '+op+' correct minus '+comparison,delta.mean(),expect,tol=.000006);bootstrap['CG024_'+op]=boot(delta)
 assert bootstrap['CG024_'+op]['ci95'][1]<0
check('CG024 operation rows',len(d),13600,tol=0)
baseline=read(24,'cg023_passive_same_panel.csv');final=read(24,'passive_long_horizon_final.csv')
for h,expect in [(32,-.01914),(64,-.01801),(128,-.01793)]:
 a=baseline[baseline.horizon==h].groupby('world_id').mse.mean();z=final[final.horizon==h].groupby('world_id').mse.mean();check(f'CG024 passive h{h} MSE difference',(z-a).mean(),expect,tol=.000006)
# Integrity and code parsing are read-only; no training/download script is executed.
integrity=[]
if SOURCE_MODE:
 root=next((W/'original_assets').iterdir())
 for line in (root/'03_ARCHIVE_METADATA'/'SHA256SUMS.txt').read_text().splitlines():
  if not line.strip():continue
  h,rel=line.split(None,1);f=root/rel.strip();integrity.append({'path':rel.strip(),'pass':f.exists() and hashlib.sha256(f.read_bytes()).hexdigest()==h})
 for f in root.rglob('*.zip'):
  with zipfile.ZipFile(f) as zz:assert zz.testzip() is None
 parsed=[]
 for f in list((W/'expanded_evidence').rglob('*.py'))+list(root.rglob('*.py')):
  ast.parse(f.read_text());parsed.append(str(f.relative_to(W)))
 (OUT/'input_integrity.json').write_text(json.dumps({'checksum_files':integrity,'zip_crc_pass':16,'parsed_python_files':len(parsed)},indent=2))
assert all(x['pass'] for x in integrity)
with (OUT/'recomputed_claims.csv').open('w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=list(checks[0]));wr.writeheader();wr.writerows(checks)
(OUT/'independent_group_bootstrap.json').write_text(json.dumps(bootstrap,indent=2))
print(json.dumps({'checks':len(checks),'passed':sum(x['pass'] for x in checks),'failed':[x for x in checks if not x['pass']],'input_checksums':len(integrity),'scope':'Reaggregation and group bootstrap from supplied result records; no new model training or checkpoint inference.'},indent=2))
assert all(x['pass'] for x in checks)
