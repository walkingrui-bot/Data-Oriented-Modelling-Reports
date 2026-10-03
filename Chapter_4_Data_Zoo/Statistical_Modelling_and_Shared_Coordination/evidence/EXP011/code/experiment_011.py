#!/usr/bin/env python3
"""INTERNAL_COORDINATION_011 reproduction scaffold."""
from __future__ import annotations
import io, urllib.request
import numpy as np
import pandas as pd
import torch
from torch import nn

URL = "https://raw.githubusercontent.com/vi-c-ky/Human-genetic-evidence-associated-with-drug-approval/main/data/final_dataset.csv"
CHANNELS = ["literature","somatic_mutation","affected_pathway","rna_expression","genetic_association","animal_model"]

def fnv1a32(text: str) -> int:
    h = 2166136261
    for ch in text:
        h ^= ord(ch)
        h = (h * 16777619) & 0xffffffff
    return h

def split_name(target: str) -> str:
    z = fnv1a32(str(target)) % 100
    return "train" if z < 70 else ("validation" if z < 85 else "test")

def load():
    with urllib.request.urlopen(URL) as r:
        df = pd.read_csv(io.BytesIO(r.read()))
    return df[["ensembl_id","efo_id_norm","label",*CHANNELS]].copy()

def make_cube(df):
    df=df.copy()
    df["split"]=df["ensembl_id"].map(split_name)
    scores=df[CHANNELS].fillna(0).clip(0,1).to_numpy()
    present=(scores>0).astype(np.int64)
    masks=np.zeros(len(df),dtype=np.int64)
    for j in range(6):
        masks |= (present[:,j] << j)
    df["mask"]=masks
    for j,c in enumerate(CHANNELS):
        df[c]=scores[:,j]
    named={c:(c,"mean") for c in CHANNELS}
    return df.groupby(["split","mask"]).agg(n=("label","size"),pos=("label","sum"),**named).reset_index()

class Ganglion(nn.Module):
    def __init__(self,d=16):
        super().__init__()
        self.enc=nn.ModuleList([nn.Linear(2,d) for _ in range(6)])
        self.core=nn.Linear(d,d)
        self.out=nn.Linear(d,1)
    def forward(self,score,present):
        es=[]
        for c in range(6):
            x=torch.stack([score[:,c],present[:,c]],dim=-1)
            es.append(torch.tanh(self.enc[c](x)))
        state=torch.stack(es).mean(0)
        state=torch.tanh(self.core(state))
        return self.out(state).squeeze(-1),state

if __name__=="__main__":
    df=load()
    cube=make_cube(df)
    print("Rows:",len(df))
    print(cube.groupby("split")["n"].sum())
    print("Input channels:",CHANNELS)
    print("Terminal-leakage fields excluded: clinical, overall_score")
    print("See protocol.json and results/results_summary.json for the reported fixed training run.")
