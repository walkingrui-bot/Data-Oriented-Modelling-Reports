from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle,FancyArrowPatch

import os
OUT=Path(os.environ.get('MDM_FIGURE_OUTPUT_DIR', str(Path.cwd()/'mdm_english_figures')))
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.titlesize':14,'axes.labelsize':12,'xtick.labelsize':11,'ytick.labelsize':11,'legend.fontsize':10,'figure.dpi':160,'savefig.dpi':230,'axes.spines.top':False,'axes.spines.right':False})
records={}
def grouped(n,title,labels,series,values,ylabel,ylim,fmt='.2f'):
    x=np.arange(len(labels)); width=.78/len(series)
    fig,ax=plt.subplots(figsize=(9.4,5.35))
    for k,(label,val) in enumerate(zip(series,values)):
        b=ax.bar(x+(k-(len(series)-1)/2)*width,val,width,label=label)
        ax.bar_label(b,labels=[format(v,fmt) for v in val],padding=3,fontsize=10)
    ax.set_xticks(x,labels); ax.set_ylabel(ylabel); ax.set_title(title,pad=16); ax.set_ylim(*ylim)
    ax.grid(axis='y',alpha=.18); ax.set_axisbelow(True)
    if len(series)>1:ax.legend(loc='upper left',bbox_to_anchor=(0,1),frameon=False,ncol=min(3,len(series)))
    fig.tight_layout();fig.savefig(OUT/f'figure_{n:02d}.png');plt.close(fig)
    records[str(n)]={'labels':labels,'series':series,'values':values,'source':'Numbers printed on the source report figure; English labels redrawn without changing reported values.','axis':ylabel,'ylim':ylim}

grouped(2,'Occupancy of low density regions',['Breast Cancer','Digits'],['Original geometry','Global attention','Local attention'],[[9.67,6.24],[13.36,13.56],[7.56,4.89]],'Observations in the designated gap (%)',(0,16))
grouped(3,'Retention of original 10 nearest neighbours',['Iris','Wine','Breast Cancer','Digits'],['Global attention','Local attention'],[[54.7,51.0,37.7,58.1],[61.4,63.4,49.2,62.9]],'Neighbour retention (%)',(0,76),'.1f')
grouped(4,'Preservation of neighbourhood ranks',['Iris','Wine','Breast Cancer','Digits'],['Global attention','Local attention'],[[.931,.931,.918,.988],[.946,.967,.945,.994]],'Trustworthiness',(.87,1.015),'.3f')
grouped(5,'Separation of mutual kNN components',['Wine','Digits'],['Original geometry','Global attention','Local attention'],[[1.98,2.06],[.91,.58],[1.47,2.86]],'Between component gap / within component scale',(0,3.45))
grouped(6,'Classification with elastic local scales',['Breast Cancer','Digits','Iris','Wine'],['Euclidean','Elastic arithmetic scale','Elastic geometric scale'],[[95.53,96.21,95.75,96.06],[96.36,97.42,96.74,98.06],[96.41,97.28,96.42,98.52]],'Accuracy (%)',(93,100))
grouped(7,'Classification in the sparsest quartile',['Breast Cancer','Digits','Wine'],['Euclidean','Elastic arithmetic scale','Elastic geometric scale'],[[97.92,89.71,85.42],[98.61,92.70,92.71],[98.96,92.37,94.79]],'Sparse quartile accuracy (%)',(80,102))
grouped(8,'Diabetes regression with elastic local scales',[r'$R^2$ × 100','Overall RMSE','Sparse quartile RMSE'],['Euclidean','Elastic local scale'],[[42.48,57.50,57.77],[43.82,56.81,56.12]],'Reported value (compare within each pair)',(0,67))
grouped(9,'Graph label propagation with 10% labels',['Iris','Wine','Breast Cancer','Digits'],['Euclidean graph','SpringGraph'],[[90.07,95.00,94.38,95.62],[91.41,97.25,94.88,96.19]],'Propagation accuracy (%)',(88,99.3))
grouped(10,'Task level selection of local scale',['Breast Cancer','Digits','Iris','Wine'],['Euclidean baseline','Scale router'],[[95.72,95.83,96.50,97.22],[96.05,96.94,96.94,97.78]],'Outer test accuracy (%)',(94.5,99))
grouped(11,'Observed coverage of Diabetes BMI',['1','2','3','4','5','6','7'],['Observations'],[[58,130,124,71,44,12,3]],'Number of observations',(0,151),'.0f')
grouped(12,'Diabetes BMI training across 50 random splits',['Overall RMSE','Macro RMSE'],['Ordinary training','Coverage balanced training'],[[64.01,65.43],[63.37,60.22]],'RMSE',(56,69))

# Schematics transcribe the operations and branches in source Figures 1 and 13.
def box(ax,x,y,w,h,t,fs=11):
    ax.add_patch(Rectangle((x,y),w,h,facecolor='white',edgecolor='black',lw=1.1)); ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=fs,linespacing=1.4)
def arrow(ax,a,b,label='',offset=(0,.17)):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=13,lw=1.1,color='black'))
    if label:ax.text((a[0]+b[0])/2+offset[0],(a[1]+b[1])/2+offset[1],label,ha='center',va='center',fontsize=10)
fig,ax=plt.subplots(figsize=(10,4.7));ax.set(xlim=(0,10),ylim=(0,4.7));ax.axis('off')
box(ax,.15,2.4,2.05,1.05,'Original data\nor fixed anchor')
box(ax,2.75,2.4,2.2,1.05,'Local geometry\nM, r, τ and c')
box(ax,5.65,2.4,2.0,1.05,'Standard attention\nQKᵀ → softmax → V')
box(ax,8.2,2.4,1.65,1.05,'Residual output\nh + c Attn(h)',10.5)
arrow(ax,(2.2,2.925),(2.75,2.925));arrow(ax,(4.95,2.925),(5.65,2.925),'mask + bias',offset=(0,.8));arrow(ax,(7.65,2.925),(8.2,2.925),'gate',offset=(0,.8))
box(ax,2.7,.35,2.5,.95,'Geometry branch\nStopped gradient or\nslow anchor update',10.5)
arrow(ax,(3.85,2.4),(3.85,1.3)); ax.text(5.25,1.75,'Independent geometric reference',fontsize=10,ha='left')
fig.tight_layout();fig.savefig(OUT/'figure_01.png');plt.close(fig)
records['1']={'source':'Source Figure 1 schematic; all operation boxes and the separate geometry branch retained with English labels.'}
fig,ax=plt.subplots(figsize=(10,5.2));ax.set(xlim=(0,10),ylim=(0,5.2));ax.axis('off')
# Two rows keep the labels readable at report width while retaining the source ordering.
box(ax,.2,3.45,2.7,1.05,'Coverage and\ngeometry assessment')
box(ax,3.65,3.45,2.7,1.05,'Coverage balanced\nstructure learning')
box(ax,7.1,3.45,2.7,1.05,'Geometry constrained\nrelations or attention')
arrow(ax,(2.9,3.975),(3.65,3.975));arrow(ax,(6.35,3.975),(7.1,3.975))
box(ax,7.1,.6,2.7,1.05,'Prevalence calibration')
box(ax,3.65,.6,2.7,1.05,'Task output\nand application')
arrow(ax,(8.45,3.45),(8.45,1.65));arrow(ax,(7.1,1.125),(6.35,1.125))
box(ax,.2,.6,2.7,1.05,'Aggregation replacement\nwhen corrections\nsuppress effective mixing',10.5)
# The secondary branch exits the constrained-relation block, as in the source.
ax.plot([7.1,1.55,1.55],[2.5,2.5,1.72],color='black',lw=1.1);arrow(ax,(8.15,3.45),(7.1,2.5));arrow(ax,(1.55,1.86),(1.55,1.65))
ax.text(4.0,2.65,'Wrapper exhaustion branch',fontsize=10,ha='center')
fig.tight_layout();fig.savefig(OUT/'figure_13.png');plt.close(fig)
records['13']={'source':'Source Figure 13 schematic; operation order and aggregation-replacement branch retained; compact two-row layout.'}
(OUT/'figure_transcription.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('English scientific figures',len(records))
