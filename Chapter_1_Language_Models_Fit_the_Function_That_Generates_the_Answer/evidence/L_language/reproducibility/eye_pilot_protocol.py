"""Protocol skeleton for the OneStop/Scanpath Studio eye pilot.
Expected columns include CURRENT_FIX_INTEREST_AREA_ID, CURRENT_FIX_DURATION,
CURRENT_FIX_INDEX, participant_id, unique_trial_id. Adapt column names for full corpora.
"""
import pandas as pd

def long_regressions(df, min_distance=5):
    out=[]
    for trial,g in df.groupby('unique_trial_id'):
        g=g.sort_values('CURRENT_FIX_INDEX')
        rows=g.to_dict('records')
        for k in range(1,len(rows)):
            source=rows[k-1]['CURRENT_FIX_INTEREST_AREA_ID']
            target=rows[k]['CURRENT_FIX_INTEREST_AREA_ID']
            if source-target >= min_distance:
                out.append((trial,k,source,target))
    return out

# Archive analyses deliberately separate:
# 1) launch/gate (source duration/surprisal relative to matched forward fixations),
# 2) target selection (semantic relation + distance + salience),
# 3) post-landing state reinstatement (do not assume literal scanpath replay).
