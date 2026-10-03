from pathlib import Path
import sys, time
import pandas as pd
from batch_core import fast_run

ROOT = Path(__file__).resolve().parents[1]
CFG = {
    "self_only": ("self_only", None, 180, 0),
    "direct_binding": ("direct", None, 0, 550),
    "switch_binding": ("switch", None, 180, 700),
    "shuffled_pairing": ("shuffled", None, 180, 700),
    "switch_freeze_core": ("switch", "core", 180, 700),
    "switch_freeze_encoders": ("switch", "encoders", 180, 700),
    "switch_freeze_decoders": ("switch", "decoders", 180, 700),
    "switch_core_only": ("switch", "interfaces", 180, 700),
}

if len(sys.argv) != 2 or sys.argv[1] not in CFG:
    raise SystemExit("usage: python code/batch_conditions.py <" + "|".join(CFG) + ">")
name = sys.argv[1]
variant, freeze, pre, bind = CFG[name]
rows = []
t0 = time.time()
for seed in range(5):
    r = fast_run(seed, variant, freeze, pre, bind)
    r.update(config=name, seed=seed, variant=variant, freeze=str(freeze))
    rows.append(r)
outdir = ROOT / "reproduced_results"
outdir.mkdir(exist_ok=True)
out = outdir / f"{name}.csv"
pd.DataFrame(rows).to_csv(out, index=False)
print(f"{name}: {time.time()-t0:.1f}s -> {out}")
print(pd.DataFrame(rows)[["seed","cross_test","worst_cross_test","align_test","latent_r2_test","d_core","d_enc","d_dec"]].to_string(index=False))
