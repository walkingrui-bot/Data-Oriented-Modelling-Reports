"""Render four publication figures from released records; no model execution."""
from pathlib import Path
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

parser=argparse.ArgumentParser()
parser.add_argument('--report-dir',type=Path,default=Path(__file__).resolve().parent)
parser.add_argument('--output-dir',type=Path)
args=parser.parse_args()
P=args.report_dir;E=P/'evidence/experiments';O=args.output_dir or P/'figures';O.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
def record(cg,name):
 return min((E/f'CG{cg:03d}').rglob(name),key=lambda f:len(f.parts))

fig,ax=plt.subplots(figsize=(11,4.7));ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
labels=[('Shape geometry','Within-distribution shape\nand conditional noise'),('Change geometry','Across-environment variation\nand mechanism stability'),('Response geometry','Intervention-induced change\nand propagation')]
for x,(h,t) in zip([.17,.5,.83],labels):
 ax.add_patch(Rectangle((x-.145,.68),.29,.24,fill=False,lw=1.2));ax.text(x,.855,h,ha='center',va='center',weight='bold');ax.text(x,.76,t,ha='center',va='center',fontsize=10)
 ax.annotate('',xy=(.5,.49),xytext=(x,.68),arrowprops={'arrowstyle':'->','lw':1.2})
ax.text(.5,.44,'Reversal-breaking information',ha='center',weight='bold',fontsize=13)
ax.text(.5,.34,'Direction is distinguishable only under assumptions that exclude the reverse interpretation',ha='center',fontsize=10)
ax.annotate('',xy=(.5,.17),xytext=(.5,.27),arrowprops={'arrowstyle':'->','lw':1.2})
ax.text(.5,.10,'Geometry-conditioned causal operators',ha='center',weight='bold',fontsize=12)
fig.tight_layout();fig.savefig(O/'figure_01.png',dpi=220,bbox_inches='tight');plt.close(fig)

d=pd.read_csv(record(4,'cg004_main_grid.csv'));d=d[d.theta<=.1]
v=[(d[k]-d.accuracy_clt).abs().mean() for k in ['pred_raw','pred_fisher','pred_D']]
fig,ax=plt.subplots(figsize=(7.4,4.6));ax.bar(['Raw parameter scale','Local Fisher metric','Exact projection distance'],v,color='#2b779f');ax.set_ylabel('MAE versus moment-based accuracy');ax.set_title('Local metric correction across tangent regimes',pad=14);ax.set_ylim(0,max(v)*1.22);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
for x,y in enumerate(v):ax.text(x,y+max(v)*.025,f'{y:.6f}',ha='center',fontsize=10)
fig.tight_layout();fig.savefig(O/'figure_11.png',dpi=220,bbox_inches='tight');plt.close(fig)

m=pd.read_csv(record(22,'engineering_summary.csv'));xx=np.arange(3);width=.19
fig,ax=plt.subplots(figsize=(8.195,5))
labels={'baseline':'Baseline','broad':'Broad','balanced':'Balanced','evidence':'Evidence-coupled'}
for j,row in m.iterrows():ax.bar(xx+(j-1.5)*width,row[['original_query_nll','train_bank_nll','heldout_bank_nll']].to_numpy(float),width=width,label=labels[row.variant])
ax.set_xticks(xx,['Original query','Training operator bank','Held-out operator bank']);ax.set_ylabel('NLL (lower is better)');ax.set_title('CG-022: consequence objectives and reusable mechanisms');ax.legend(loc='lower left',fontsize=9)
fig.tight_layout();fig.savefig(O/'figure_75.png',dpi=200);plt.close(fig)

initial=pd.read_csv(record(24,'acceptance_summary_first_pass.csv'))
final=pd.read_csv(record(24,'acceptance_summary_final_complete.csv'))
ops=['impulse','clamp','persistent_force','compound_force_plus_impulse']
comparisons=['correct_minus_ignore']*3+['correct_minus_omit_second']
a=[];z=[]
for op,comparison in zip(ops,comparisons):
 a.append(float(initial[(initial.operation==op)&(initial.comparison==comparison)]['mean'].iloc[0]))
 z.append(float(final[(final.operation==op)&(final.comparison==comparison)]['mean'].iloc[0]))
fig,ax=plt.subplots(figsize=(8,8*936/1584));xx=np.arange(4);width=.36
ax.bar(xx-width/2,a,width,label='Initial event-trained model');ax.bar(xx+width/2,z,width,label='Model with consistency objectives')
ax.axhline(0,color='#4d4d4d',linewidth=.8);ax.set_xticks(xx,['Impulse','Clamp','Persistent force','Force + impulse']);ax.set_ylabel('Mean ΔMSE: correct − ignore/omit');ax.set_title('CG-024: consistency objectives improve event execution');ax.legend(loc='lower left',fontsize=9)
fig.tight_layout();fig.savefig(O/'figure_85.png',dpi=198);plt.close(fig)
print('Rendered figures 1, 11, 75 and 85 from conceptual definitions and supplied result records.')
