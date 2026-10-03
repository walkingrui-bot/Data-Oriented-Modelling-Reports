import argparse, json, random, sys, copy
from pathlib import Path
import numpy as np, torch
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import model_and_data as m

RUNS={
 1: dict(init=1,self_seed=2,bind_seed=920,shuffle_seed=1020),
 2: dict(init=2,self_seed=201,bind_seed=203,shuffle_seed=204),
 3: dict(init=3,self_seed=301,bind_seed=303,shuffle_seed=304),
}

def evaluate(model):
    test=m.ALL_SCENES[1000:1200]
    return {**m.zmetrics(m.allZ(model,test),test), **m.pairs(model,test)}

def run(run_id, outdir, smoke=False):
    cfg=RUNS[run_id]; train=m.ALL_SCENES[:800]
    torch.manual_seed(cfg['init']); random.seed(cfg['init']); np.random.seed(cfg['init'])
    model=m.M().to(m.DEVICE)
    ss,bs= (5,8) if smoke else (600,650)
    m.train(model,train,ss,cfg['self_seed'],'self',B=64,trace=max(1,ss//4))
    self_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}; self_metrics=evaluate(model)
    m.train(model,train,bs,cfg['bind_seed'],'bind',B=64,trace=max(1,bs//4)); bind_metrics=evaluate(model)
    sh=m.M().to(m.DEVICE); sh.load_state_dict(self_state); m.train(sh,train,bs,cfg['shuffle_seed'],'shuffle',B=64,trace=max(1,bs//4)); shuffle_metrics=evaluate(sh)
    outdir.mkdir(parents=True,exist_ok=True)
    json.dump({'run':run_id,'self':self_metrics,'bind':bind_metrics,'shuffle':shuffle_metrics},open(outdir/f'run{run_id}_metrics.json','w'),indent=2)
    torch.save({'self':self_state,'bind':model.state_dict(),'shuffle':sh.state_dict()},outdir/f'run{run_id}_states.pt')

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--run',type=int,choices=[1,2,3],required=True); ap.add_argument('--out',default='reproduced'); ap.add_argument('--smoke',action='store_true'); a=ap.parse_args()
    run(a.run,Path(a.out),a.smoke)
