from pathlib import Path
import json
import pandas as pd, numpy as np
ROOT=Path(__file__).resolve().parent
# This script rebuilds compact machine-readable summaries from the completed tables.
base=pd.read_csv(ROOT/'eval_detail.csv')
agg=base.groupby(['presentation','regime','horizon','model'],as_index=False).mse.mean()
agg.to_csv(ROOT/'base_eval_summary.csv',index=False)
roll=pd.read_csv(ROOT/'world_rollout.csv').groupby('step',as_index=False).M_step_rms.mean()
summary={
 'base_eval_rows':int(len(base)),
 'test_worlds':int(base.world_id.nunique()),
 'seeds':sorted(map(int,base.seed.unique())),
 'world_update20_mean_M_step_rms':float(roll.loc[roll.step==20,'M_step_rms'].iloc[0]),
 'mixed_h32_world_mse':float(agg.query("presentation=='mixed' and regime=='temp' and horizon==32 and model=='world'").mse.iloc[0]),
 'mixed_h32_direct_mse':float(agg.query("presentation=='mixed' and regime=='temp' and horizon==32 and model=='direct'").mse.iloc[0]),
}
(ROOT/'analysis_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
