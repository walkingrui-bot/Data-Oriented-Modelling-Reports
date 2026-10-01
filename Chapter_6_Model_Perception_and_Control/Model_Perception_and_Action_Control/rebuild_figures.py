"""Rebuild the English charts from reported values; no external data is downloaded.
Requires numpy, matplotlib and Pillow. Run from any working directory.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
ROOT = Path(__file__).resolve().parent
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)

# Rebuild the first ten source figures with English labels and the reported values.
# Other figures are retained in the publication; this script rebuilds the 14 identified charts.
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.titlesize':12,'savefig.dpi':180})
def canvas():return plt.subplots(figsize=(8.4,4.6),layout='constrained')
def save(n,fig):
    fig.savefig(FIG/f'figure_{n:02d}.png',facecolor='white');plt.close(fig)
def bars(n,labels,values,ylabel,title,ylim=None,fmt=None):
    fig,ax=canvas();bs=ax.bar(labels,values,color='#2471a3');ax.set(ylabel=ylabel,title=title)
    if ylim:ax.set_ylim(*ylim)
    if fmt:ax.bar_label(bs,labels=[fmt.format(x) for x in values],padding=4,fontsize=10)
    save(n,fig)
fig,ax=canvas();vals=[1.163/.928,109/20.6,44/.23];b=ax.bar(['Window Fano','Repeated bigrams','Repeated trigrams'],vals,color='#2471a3');ax.set_yscale('log');ax.set_ylim(.8,400);ax.set(ylabel='Observed / permutation mean (log scale)',title='Local clustering beyond global frequency');ax.bar_label(b,labels=[f'{v:.1f}×' for v in vals],padding=4);save(1,fig)
fig,ax=canvas();x=np.arange(4);ax.bar(x-.19,[.912,.485,.2985,.4031],.38,label='Before correction');ax.bar(x+.19,[.983,.220,.1349,.2121],.38,label='After correction');ax.set_xticks(x,['Normalized\nentropy','Gini','Top 5%\nmass','Top 10%\nmass']);ax.set(ylabel='Statistic / mass fraction',title='Redistribution of effective statistical mass',ylim=(0,1.13));ax.legend(frameon=False);save(2,fig)
bars(3,['Action entropy','Transition entropy','Repeated bigrams','Repeated trigrams'],[.095,.019,-.031,-.051],'Resolved minus unresolved','Length-matched trajectory differences',(-.07,.12),'{:+.3f}')
fig,ax=canvas();ax.plot(['Early','Middle','Late'],[77,102,129],'o-');ax.set(ylabel='Mean words per reasoning chunk',title='Working-language length across task phases',ylim=(60,140));[ax.annotate(str(v),(i,v),xytext=(0,8),textcoords='offset points',ha='center') for i,v in enumerate([77,102,129])];save(4,fig)
fig,ax=canvas()
for label,v in [('First-person density',[6,5.38,5.20]),('Social / filler density',[.337,.320,.222]),('Repeated bigrams',[5.19,8,7.81]),('Repeated trigrams',[.81,1.41,1.69])]:ax.plot(['Early','Middle','Late'],v,'o-',label=label)
ax.set(ylabel='Percentage',title='Working-language statistics across task phases',ylim=(0,10));ax.legend(frameon=False,ncol=2,fontsize=9,loc='upper left');save(5,fig)
labels=['Raw\nc','Square root\nc$^{0.5}$','Quarter power\nc$^{0.25}$','Role aware']
bars(6,labels,[7.449,5.963,5.555,5.512],'Leave-one-trajectory-out NLL','Sublinear exposure in next-action prediction',(0,8.5),'{:.3f}')
bars(7,labels,[46.15,46.15,47.01,47.86],'Next-action accuracy (%)','Accuracy under exposure corrections',(0,55),'{:.2f}%')
fig,ax=canvas();x=np.arange(4)
for j,(lab,v) in enumerate([('Raw global attention',[80.3,84.2,94.9,98.1]),('Geometry lens',[18.5,52.2,71,66.6]),('Topology lens',[0,0,0,0])]):ax.bar(x+(j-1)*.24,v,.24,label=lab)
ax.set_xticks(x,['Iris','Wine','Breast Cancer','Digits']);ax.set(ylabel='Mass outside the reference 15-NN (%)',title='Geometry and permitted connectivity',ylim=(0,115));ax.legend(frameon=False,ncol=3,fontsize=9,loc='upper left');save(8,fig)
bars(9,['Raw','Geometry','Topology','Geometry +\nTopology'],[65.80,92.20,93.65,93.92],'Mean accuracy with 10% labels (%)','Label propagation with the same attention kernel',(0,110),'{:.2f}%')
fig,ax=plt.subplots(figsize=(9.2,2.6),layout='constrained');ax.set(xlim=(0,10.5),ylim=(0,2));ax.axis('off')
labels=['Surface language\nor numerical data','Role\nidentification','Sublinear\nexposure','Topology and\ngeometry','Standard\nattention']
for i,label in enumerate(labels):
    x=.1+i*2.1;ax.add_patch(Rectangle((x,.75),1.8,.8,fill=False,lw=1.2));ax.text(x+.9,1.15,label,ha='center',va='center',fontsize=10)
    if i<4:ax.annotate('',xy=(x+2.04,1.15),xytext=(x+1.84,1.15),arrowprops={'arrowstyle':'->'})
ax.text(5.25,.25,'Calibrate how observed statistics become internal importance.',ha='center',fontsize=11);save(10,fig)


# Repair four charts while preserving their measured values and aspect ratios.
rebuilt=set(range(1,11))|{15,35,47,54}
def source_canvas(n):
    w,h=Image.open(ROOT/f'evidence/original_figures/figure_{n:02d}_source.png').size
    return plt.subplots(figsize=(w/180,h/180),layout='constrained')
fig,ax=source_canvas(15);x=np.arange(3)
b1=ax.bar(x-.18,[5.59,3.22,9.43],.36,label='Estimated gain',color='#1f77b4')
b2=ax.bar(x+.18,[8.29,8.22,8.22],.36,label='One standard error',color='#ff7f0e')
ax.bar_label(b1,fmt='%.2f',padding=3,fontsize=10);ax.bar_label(b2,fmt='%.2f',padding=3,fontsize=10)
ax.set_xticks(x,['Batch A','Batch B','Batch C']);ax.set(ylabel='Percentage points',ylim=(0,13),title='ASTIG-009: switchability and sampling uncertainty')
ax.legend(loc='upper left',frameon=False,ncol=2,fontsize=10)
for i,label in enumerate(['Routed states: 0%','Routed states: 0%','Routed states: 73.81%']):ax.text(i,-.15,label,transform=ax.get_xaxis_transform(),ha='center',fontsize=9)
save(15,fig)
fig,ax=source_canvas(35);bs=ax.bar(['Prior edit','Post-edit\nverification','Formal post-edit\ntest','Latest formal test\nreturn code 0'],[20,20,12,11],color='#1f77b4')
ax.bar_label(bs,labels=['20/20','20/20','12/20','11/20'],padding=4)
ax.set(ylabel='Submitted trajectories (n = 20)',ylim=(0,23),title='Observed prerequisites in recorded Submitted trajectories');save(35,fig)
fig,ax=source_canvas(47);ax2=ax.twinx();layers=list(range(9))
l1=ax.plot(layers,[.0513,.0534,.0580,.0640,.0720,.0850,.1104,.1337,.1508],'o-',color='#1f77b4',label='Fisher ratio')
l2=ax2.plot(layers,[.5500,.5524,.5310,.5452,.5381,.5143,.5190,.5048,.5071],'s-',color='#d2691e',label='5-NN cross-mode mixing')
ax.set(xlabel='Layer',ylabel='Fisher ratio',ylim=(.045,.18),title='Decision-state geometry across layers');ax2.set(ylabel='Cross-mode neighbour fraction',ylim=(.50,.568))
ax.legend(l1+l2,[l.get_label() for l in l1+l2],loc='upper center',frameon=False,ncol=2,fontsize=9);save(47,fig)
fig,ax=source_canvas(54);x=np.arange(3)
ax.bar(x-.24,[1.8110,1.8509,1.8571],.24,label='Mode-axis C')
ax.bar(x,[.0518,.0376,.0262],.24,label='Orthogonal control 95th percentile')
ax.bar(x+.24,[.1380,.2765,.1824],.24,label='Label-swap control 95th percentile')
ax.set_xticks(x,['Block 21','Block 22','Block 23']);ax.set(ylabel='Control effect C',ylim=(0,2.5),title='Selective causal control and matched control distributions')
ax.legend(loc='upper center',frameon=False,fontsize=10);save(54,fig)
