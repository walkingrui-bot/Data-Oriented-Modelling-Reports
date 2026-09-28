"""Reproducibility sketch for MDM-KERNEL-002.
Uses NetworkX built-in real networks and scikit-learn metrics.
The archived CSVs contain the executed 100-split outputs.
"""
import networkx as nx
import numpy as np
# Protocol summary:
# 1. Load nx.karate_club_graph(), nx.davis_southern_women_graph(),
#    nx.florentine_families_graph().
# 2. For each seed, withhold ~15% edges while preserving endpoint degree;
#    preserve connectivity in one-mode graphs.
# 3. Rank withheld edges among currently absent legal candidate pairs.
# 4. Compare local Attention-state proposal, low-rank SVD, and
#    mechanism-native relation kernels; evaluate AUC, AP and Recall@k.
# 5. On Davis, additionally score A^p for p in {1,2,3,4,5,7}.
# Full numerical outputs are stored in the CSV files in this bundle.
