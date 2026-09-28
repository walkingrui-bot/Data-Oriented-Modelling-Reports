"""Reconcile published split-level measurements using only the Python standard library."""
from pathlib import Path
import csv,hashlib,json,math,sys

ROOT=Path(__file__).resolve().parent.parent
expected=json.loads((ROOT/'verification/recorded_result_means.json').read_text())
E=ROOT/'evidence/experiments'
BLIND=E/'MDM-SOP-BLIND-VALIDATION-003'
KERNEL=E/'MDM-KERNEL-002'
checked=0
def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def equal(a,b,label):
    global checked
    assert math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-11),(label,a,b)
    checked+=1
def mean(rs,key):return sum(float(r[key]) for r in rs)/len(rs)

for name in ['modechoice_blind_results','engel_blind_results','randhie_blind_results','lesmis_blind_results','engel_nested_microprobe']:
    rs=rows(BLIND/(name+'.csv'));ex=expected[name]
    assert len(rs)==ex['n'],name
    for key,value in ex['means'].items():equal(mean(rs,key),value,name+'/'+key)
    if name=='modechoice_blind_results':equal(sum(float(r['conditional_set_nll'])<float(r['flat_set_nll']) for r in rs)/len(rs),ex['nll_win_rate'],'modechoice win fraction')
    if name=='randhie_blind_results':equal(sum(float(r['poisson_poisson_deviance'])<float(r['ridge_poisson_deviance']) for r in rs)/len(rs),ex['deviance_win_rate'],'randhie win fraction')
    if name=='lesmis_blind_results':equal(sum(float(r['AA_auc'])>float(r['PA_auc']) for r in rs),ex['aa_wins'],'lesmis win count')
    if name=='engel_nested_microprobe':
        for key,value in ex['choices'].items():equal(sum(r['choice']==key for r in rs),value,'nested choice '+key)

for name in ['graph_edge_recovery_100splits','davis_path_order_100splits','one_mode_extra_kernels_100splits']:
    rs=rows(KERNEL/(name+'.csv'))
    for group in expected[name]:
        matched=[r for r in rs if all(r[k]==str(v) for k,v in group['group'].items())]
        assert len(matched)==group['n'],group
        for metric in ['AUC','AP','Recall@k']:equal(mean(matched,metric),group[metric],name+'/'+str(group['group'])+'/'+metric)

pre=BLIND/'blind_precommit.json'
digest=hashlib.sha256(pre.read_bytes()).hexdigest()
assert digest==expected['precommit_sha256']==(BLIND/'blind_precommit.sha256').read_text().split()[0]
preserved=json.loads((ROOT/'verification/numeric_table_preservation.json').read_text())
assert preserved['count']==179 and all(r['match'] for r in preserved['checks'])
print(json.dumps({'result':'passed','recalculated_values_and_counts':checked,'source_numeric_table_cells_preserved':179,'precommit_sha256':digest},indent=2))
