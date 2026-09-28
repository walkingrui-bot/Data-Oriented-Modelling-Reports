import os
from pathlib import Path
import json, hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SRC=Path(os.environ.get('B3_INPUT_DIR', str(Path(__file__).resolve().parent.parent/'024')))
OUT=Path(os.environ.get('B3_OUTPUT_DIR', str(Path.cwd()/'reproduction_025'))); OUT.mkdir(exist_ok=True, parents=True)
scale=pd.read_csv(SRC/'active_neighbour_scale.csv')
temp=pd.read_csv(SRC/'temporal_state_geometry.csv')

# Merge measured scale tables.
df=scale.merge(temp,on=['window_days','n_windows'],how='inner')
df['effective_to_raw_coverage_ratio']=df['median_effective_static_coverage']/df['median_coverage']
df['effective_to_active_partner_ratio']=df['median_effective_partners']/df['median_active_partners']
df['node_dyad_continuity_gap']=df['node_consecutive_cosine']-df['dyad_consecutive_cosine']
df['dyad_to_node_entropy_rank_ratio']=df['dyad_entropy_effective_rank']/df['node_entropy_effective_rank']
df['node_to_dyad_top1_share_ratio']=df['node_top1_share']/df['dyad_top1_share']

def logfit(x,y):
    x=np.asarray(x,float); y=np.asarray(y,float)
    lx=np.log(x); ly=np.log(y)
    slope, intercept=np.polyfit(lx,ly,1)
    pred=intercept+slope*lx
    ss_res=((ly-pred)**2).sum(); ss_tot=((ly-ly.mean())**2).sum()
    return {'exponent':float(slope),'prefactor':float(np.exp(intercept)),'r2_logspace':float(1-ss_res/ss_tot)}

fits={
    'median_active_neighbour_coverage':logfit(df.window_days,df.median_coverage),
    'median_active_partners':logfit(df.window_days,df.median_active_partners),
    'median_effective_partners':logfit(df.window_days,df.median_effective_partners),
    'median_effective_static_coverage':logfit(df.window_days,df.median_effective_static_coverage),
    'node_minus_dyad_continuity_gap':logfit(df.window_days,df.node_dyad_continuity_gap),
}

# Endpoint contrasts across measured scale endpoints only.
first=df.iloc[0]; last=df.iloc[-1]
contrasts={
    'window_range_days':[int(first.window_days),int(last.window_days)],
    'raw_coverage_fold':float(last.median_coverage/first.median_coverage),
    'effective_coverage_fold':float(last.median_effective_static_coverage/first.median_effective_static_coverage),
    'active_partners_fold':float(last.median_active_partners/first.median_active_partners),
    'effective_partners_fold':float(last.median_effective_partners/first.median_effective_partners),
    'effective_to_raw_coverage_ratio_start':float(first.effective_to_raw_coverage_ratio),
    'effective_to_raw_coverage_ratio_end':float(last.effective_to_raw_coverage_ratio),
    'node_dyad_continuity_gap_start':float(first.node_dyad_continuity_gap),
    'node_dyad_continuity_gap_end':float(last.node_dyad_continuity_gap),
    'dyad_to_node_entropy_rank_ratio_start':float(first.dyad_to_node_entropy_rank_ratio),
    'dyad_to_node_entropy_rank_ratio_end':float(last.dyad_to_node_entropy_rank_ratio),
    'edge_retention_start':float(first.retention),
    'edge_retention_end':float(last.retention),
    'new_edge_fraction_start':float(first.new_edge_fraction),
    'new_edge_fraction_end':float(last.new_edge_fraction),
}

df.to_csv(OUT/'rg025_multiscale_renormalization.csv',index=False)
pd.DataFrame([{**{'metric':k},**v} for k,v in fits.items()]).to_csv(OUT/'rg025_descriptive_logfits.csv',index=False)
(OUT/'rg025_summary.json').write_text(json.dumps({'fits':fits,'contrasts':contrasts,'source_files':['active_neighbour_scale.csv','temporal_state_geometry.csv'],'source_experiment':'REAL-GRAPH-ACTIVE-FIELD-GEOMETRY-024','note':'Fits are descriptive across five measured window scales (7,14,30,60,90 days), not universal power laws.'},indent=2),encoding='utf-8')

# Figures: no style presets, matplotlib defaults.
fig,ax=plt.subplots(figsize=(7.2,4.8))
ax.plot(df.window_days,df.median_coverage,marker='o',label='raw active-neighbour coverage')
ax.plot(df.window_days,df.median_effective_static_coverage,marker='o',label='effective static coverage')
ax.set_xscale('log'); ax.set_xlabel('Window length (days)'); ax.set_ylabel('Median fraction of lifetime neighbours')
ax.set_title('Active neighbourhood grows faster than effective occupied neighbourhood')
ax.legend(); fig.tight_layout(); fig.savefig(OUT/'fig025A_coverage_scaling.png',dpi=180); plt.close(fig)

fig,ax=plt.subplots(figsize=(7.2,4.8))
ax.plot(df.window_days,df.median_active_partners,marker='o',label='active partners')
ax.plot(df.window_days,df.median_effective_partners,marker='o',label='effective partners')
ax.set_xscale('log'); ax.set_xlabel('Window length (days)'); ax.set_ylabel('Median partner count')
ax.set_title('Longer windows add partners faster than they add effective traffic support')
ax.legend(); fig.tight_layout(); fig.savefig(OUT/'fig025B_partner_scaling.png',dpi=180); plt.close(fig)

fig,ax=plt.subplots(figsize=(7.2,4.8))
ax.plot(df.window_days,df.node_consecutive_cosine,marker='o',label='node state')
ax.plot(df.window_days,df.dyad_consecutive_cosine,marker='o',label='directed-dyad state')
ax.plot(df.window_days,df.node_dyad_continuity_gap,marker='o',label='node - dyad gap')
ax.set_xscale('log'); ax.set_xlabel('Window length (days)'); ax.set_ylabel('Adjacent-window cosine / gap')
ax.set_title('Coarse-graining narrows but does not erase node-dyad timescale separation')
ax.legend(); fig.tight_layout(); fig.savefig(OUT/'fig025C_continuity_scaling.png',dpi=180); plt.close(fig)

fig,ax=plt.subplots(figsize=(7.2,4.8))
ax.plot(df.window_days,df.retention,marker='o',label='prior-edge retention')
ax.plot(df.window_days,df.new_edge_fraction,marker='o',label='new-edge fraction')
ax.plot(df.window_days,df.edge_jaccard,marker='o',label='edge-set Jaccard')
ax.set_xscale('log'); ax.set_xlabel('Window length (days)'); ax.set_ylabel('Fraction')
ax.set_title('Relation turnover remains substantial even under 90-day coarse-graining')
ax.legend(); fig.tight_layout(); fig.savefig(OUT/'fig025D_turnover_scaling.png',dpi=180); plt.close(fig)

fig,ax=plt.subplots(figsize=(7.2,4.8))
ax.plot(df.window_days,df.dyad_to_node_entropy_rank_ratio,marker='o',label='dyad / node entropy-rank ratio')
ax.plot(df.window_days,df.node_to_dyad_top1_share_ratio,marker='o',label='node / dyad top-1 variance-share ratio')
ax.axhline(1,linewidth=1)
ax.set_xscale('log'); ax.set_xlabel('Window length (days)'); ax.set_ylabel('Ratio')
ax.set_title('Dyad state carries broader temporal support, especially at short scales')
ax.legend(); fig.tight_layout(); fig.savefig(OUT/'fig025E_spectral_ratio.png',dpi=180); plt.close(fig)
