#!/usr/bin/env python3
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.neighbors import NearestNeighbors
import statsmodels.api as sm
import networkx as nx
from scipy.spatial.distance import pdist

# Reconstructs the four raw task matrices used in EXP014A. The exact genotype
# matrix must be acquired separately; provider observations are not distributed.
import argparse
ap=argparse.ArgumentParser()
ap.add_argument('--genotype-csv',required=True)
ap.add_argument('--out',default='EXP014A_reproduced')
args=ap.parse_args()
OUT=Path(args.out); OUT.mkdir(parents=True,exist_ok=True)
g=pd.read_csv(args.genotype_csv); geno=g.iloc[:,1:].to_numpy(float)
bc=load_breast_cancer(); tab=bc.data.astype(float)
sun=sm.datasets.sunspots.load_pandas().data.SUNACTIVITY.to_numpy(float)
time=np.asarray([np.r_[sun[t-12:t],sun[t:t+3]] for t in range(12,len(sun)-2)])
kar=nx.to_numpy_array(nx.karate_club_graph(),nodelist=range(34),weight=None,dtype=float)
pd.DataFrame(geno).to_csv(OUT/'genotype.csv',index=False)
pd.DataFrame(tab).to_csv(OUT/'WDBC.csv',index=False)
pd.DataFrame(time).to_csv(OUT/'sunspots_lagged.csv',index=False)
pd.DataFrame(kar).to_csv(OUT/'karate_adjacency.csv',index=False)
print('Reconstructed matrices:',geno.shape,tab.shape,time.shape,kar.shape)
