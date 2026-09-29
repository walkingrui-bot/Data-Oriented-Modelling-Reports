import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'experiments'/'EXP002_GENOME_CAPACITY'
# Example: regenerate the primary capacity scan figure
df=pd.read_csv(root/'EXP002_capacity_scan_960snp.csv')
plt.figure(figsize=(7,4.2))
plt.plot(df['map_dof'],df['mean_test_R2'],marker='o')
plt.xlabel('Rank-constrained mapping DOF')
plt.ylabel('Mean held-out test R2')
plt.title('EXP002 capacity scan')
plt.tight_layout()
plt.savefig(root/'reproduced_EXP002.png',dpi=190)
