import importlib.util, pandas as pd
spec=importlib.util.spec_from_file_location('d','/mnt/data/INTERNAL_COORDINATION_007/code/recurrent_defs.py'); d=importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
OUT=d.OUT
old=pd.read_csv(f'{OUT}/per_seed_by_evidence.csv'); rows=[]
for mode in ['trainable','identity','fixed_random']:
 for seed in [3,4]:
  m=d.train(seed,mode)
  for r in d.score(m,seed): rows.append({'mode':mode,'seed':seed,**r})
new=pd.concat([old,pd.DataFrame(rows)],ignore_index=True); new.to_csv(f'{OUT}/per_seed_by_evidence.csv',index=False)
print(new.groupby(['mode','nobs']).median(numeric_only=True).to_string())
