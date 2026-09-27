"""Reanalysis specification for HUMAN-LEARNING-DIMENSION-002.

Usage outside this sandbox:
  1. Obtain data_all_wClickInfo.csv at Git blob
     e834ccbbe1e183b7e2c094702b50f2e9ce558441
  2. Place it next to this script.
  3. Run with Python 3 + pandas/numpy.

The checked-in report tables are the executed outputs. This script documents the
core transformation so the public raw file can be independently reprocessed.
"""
from pathlib import Path
import numpy as np, pandas as pd

p=Path(__file__).with_name('data_all_wClickInfo.csv')
df=pd.read_csv(p)
dims=['color','shape','pattern']

def trial_metrics(r):
    relevant=correct=0
    for d in dims:
        if bool(r[f'ifRelevantDimension_{d}']):
            relevant += 1
            correct += int(r[f'builtFeature_{d}']==r[f'rewardingFeature_{d}'])
    relmatch=correct/relevant
    return pd.Series({'relevant_match':relmatch,'expected_reward':0.2+0.6*relmatch})

m=df.apply(trial_metrics,axis=1)
df=pd.concat([df,m],axis=1)
participant_perf=df.groupby('workerId').expected_reward.mean()
keep=participant_perf[participant_perf>=0.468].index
df=df[df.workerId.isin(keep)].copy()
print('participants',df.workerId.nunique(),'trials',len(df))
print(df.groupby(['numRelevantDimensions','informed']).agg(
    expected_reward=('expected_reward','mean'),
    median_rt=('rt','median'),
    mean_selected_dims=('numSelectedFeatures','mean')
))
