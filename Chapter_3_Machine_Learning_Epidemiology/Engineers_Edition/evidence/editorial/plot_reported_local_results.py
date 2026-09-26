#!/usr/bin/env python3
"""Draw exact aggregate values transcribed from the supplied local reports."""
from pathlib import Path
import argparse
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
args = parser.parse_args()
root=args.root.resolve();figdir=root/"figures"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,
                     "axes.spines.right":False,"figure.facecolor":"white","axes.titleweight":"bold"})
blue, teal, orange, gray = "#22577A", "#247B7B", "#C66A32", "#727C83"

blocks=[6,15,24,29]
series={"Full state patch":[.9884,.9733,-.3073,-1.4946],
        "Gradient projection":[.9907,.9721,-.1055,-.3598],
        "Equal-norm random":[.9980,.9979,.9193,1.0239]}
fig,ax=plt.subplots(figsize=(7.0,3.7),layout="constrained")
x=np.arange(4);width=.24
for i,(name,values) in enumerate(series.items()):
    bars=ax.bar(x+(i-1)*width,values,width,label=name,color=[blue,teal,orange][i])
    ax.bar_label(bars,fmt="%.3f",fontsize=8,padding=3)
ax.axhline(0,color="#222222",linewidth=.8)
ax.axhline(.9984,color=gray,linestyle="--",linewidth=1,label="Original margin 0.9984")
ax.set(xticks=x,xticklabels=blocks,xlabel="Block numbered from one",ylabel="Wrong minus correct tool margin",
       title="One pretrained case at four sampled blocks",ylim=(-1.9,1.55))
ax.legend(ncol=2,loc="lower center",bbox_to_anchor=(.5,-.44),frameon=False,fontsize=8)
fig.savefig(figdir/"local_pretrained_patch.png",dpi=240,bbox_inches="tight");plt.close(fig)

fig,ax=plt.subplots(figsize=(7.0,3.8),layout="constrained")
names=["135M\noriginal labels","135M\nprefixed labels","22.7M\nrelevance ranker","TF-IDF\nlexical matching"]
selection_values=[40,37,99,99]
bars=ax.bar(names,selection_values,color=[gray,gray,blue,teal],width=.58)
ax.bar_label(bars,labels=[f"{v}/100" for v in selection_values],padding=4,fontsize=11)
ax.set(ylabel="Correct selections out of 100",ylim=(0,113),title="Frozen comparison on 100 BFCL tasks")
ax.set_yticks([0,25,50,75,100]);fig.savefig(figdir/"local_selection_accuracy.png",dpi=240);plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(7.0,3.8),layout="constrained")
x=np.arange(2)
for j,(values,label,color) in enumerate([([100,95],"Relevance",blue),([100,85],"Lexical",teal)]):
    b=axs[0].bar(x+(j-.5)*.3,values,.3,label=label,color=color)
    axs[0].bar_label(b,labels=[f"{int(v*.4)}/40" for v in values],padding=3,fontsize=9)
axs[0].set(xticks=x,xticklabels=["Original","Paraphrase"],ylim=(0,114),ylabel="Accuracy percent",title="Candidate ranking")
axs[0].legend(loc="lower left",frameon=True,facecolor="white",edgecolor="white",framealpha=1,fontsize=9)
b=axs[1].bar(["Original","Paraphrase"],[30,5],color=[blue,orange],width=.55)
axs[1].bar_label(b,labels=["12/40","2/40"],padding=4)
axs[1].set(ylim=(0,40),ylabel="Accepted coverage percent",title="Same frozen rejection policy")
fig.savefig(figdir/"local_paraphrase_stress.png",dpi=240);plt.close(fig)

records=[]
for i,b in enumerate(blocks):
    for name,vs in series.items():records.append(["MCD-ENGINEERING-20260926-001",f"multiple_23 block {b}",name,vs[i],"wrong-minus-correct margin"])
for name,value in zip(names,selection_values):
    records.append(["MCD-SELECTION-20260926-002","multiple_60..159",name.replace("\n"," "),value,"correct out of 100"])
for condition,method,correct in [("original","relevance",40),("original","lexical",40),("paraphrase","relevance",38),("paraphrase","lexical",34)]:
    records.append(["MCD-SEMANTIC-STRESS-20260926-003",condition,method,correct,"correct out of 40"])
for condition,n in [("original",12),("paraphrase",2)]:
    records.append(["MCD-SEMANTIC-STRESS-20260926-003",condition,"frozen rejection policy",n,"accepted out of 40"])
with (root/"evidence/editorial/reported_local_figure_values.csv").open("w",newline="") as f:
    w=csv.writer(f);w.writerow(["study_id","condition","method","value","unit"]);w.writerows(records)
print("Created three figures and the attributed aggregate-value table.")
