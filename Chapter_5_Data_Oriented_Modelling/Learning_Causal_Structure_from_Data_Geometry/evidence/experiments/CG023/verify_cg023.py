from pathlib import Path
import json, sys
import numpy as np, torch
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import run_cg023_coordinate_world as cg

def fixed_mixed(eqbank,tmbank,ids):
    C=[]; K=[]
    for w in ids:
        C.append(np.concatenate([eqbank[w,:4],tmbank[w,:4]],0))
        K.append(np.r_[np.zeros(4,int),np.ones(4,int)])
    return torch.tensor(np.stack(C),dtype=torch.float32),torch.tensor(np.stack(K),dtype=torch.long)

def main():
    torch.set_num_threads(4)
    z=np.load(ROOT/'world_data.npz'); Mtrue=z['M']; btrue=z['b']; eq=z['eqbank']; tm=z['tmbank']; ids=np.arange(500,564)
    C,K=fixed_mixed(eq,tm,ids)
    # fixed temporal h=16 queries
    rng=np.random.default_rng(23023); x0=rng.uniform(-1.3,1.3,(len(ids),cg.D)).astype('float32')
    q=np.zeros((len(ids),2+cg.D+2),np.float32);q[:,1]=1;q[:,2:2+cg.D]=x0;q[:,-2]=4.
    Q=torch.tensor(q)
    out={}
    for seed in [11,22]:
        ck=torch.load(ROOT/'models'/f'cg023_{seed}.pt',map_location='cpu',weights_only=False)
        w=cg.WorldProgram();d=cg.DirectAttention();w.load_state_dict(ck['world']);d.load_state_dict(ck['direct']);w.eval();d.eval()
        with torch.no_grad():
            # explicit-state replay
            _,_,_,tr=w.form_world(C,K,steps=2,trace=True)
            st=(tr['M'][:,-1].clone(),tr['b'][:,-1].clone(),tr['logits'][:,-1].clone())
            M2,b2,l2=w.form_world(C,K,steps=2,start_state=st)
            M4,b4,l4=w.form_world(C,K,steps=4)
            replay=max(float((M2-M4).abs().max()),float((b2-b4).abs().max()),float((l2-l4).abs().max()))
            # container reversal: same evidence set, reversed array order
            pw,_=cg.world_predict(w,C,K,Q,steps=4);pd=d(C,K,Q)
            Cr=torch.flip(C,[1]);Kr=torch.flip(K,[1])
            pwr,_=cg.world_predict(w,Cr,Kr,Q,steps=4);pdr=d(Cr,Kr,Q)
            wperm=float((pw-pwr).abs().max());dperm=float((pd-pdr).abs().max())
            M,b,l=w.form_world(C,K,steps=4);rowsum=float(M.abs().sum(-1).max())
        out[str(seed)]={
          'selected_world_step':int(ck['selected_world_step']),
          'selected_direct_step':int(ck['selected_direct_step']),
          'state_replay_max_abs':replay,
          'world_container_reverse_max_pred_abs':wperm,
          'direct_container_reverse_max_pred_abs':dperm,
          'max_relation_row_abs_sum':rowsum,
          'world_parameters':sum(p.numel() for p in w.parameters()),
          'direct_parameters':sum(p.numel() for p in d.parameters())
        }
    out['checks']={
      'both_runs_registered_to_700':all(len(json.loads((ROOT/'models'/f'cg023_{s}_training.json').read_text()))==14 for s in [11,22]),
      'state_replay_exact':all(v['state_replay_max_abs']==0 for k,v in out.items() if k in ['11','22']),
      'container_invariance_numeric':all(max(v['world_container_reverse_max_pred_abs'],v['direct_container_reverse_max_pred_abs'])<1e-5 for k,v in out.items() if k in ['11','22']),
      'relation_constraint_satisfied':all(v['max_relation_row_abs_sum']<=0.950001 for k,v in out.items() if k in ['11','22'])
    }
    (ROOT/'verification.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))
    if not all(out['checks'].values()): raise SystemExit(1)
if __name__=='__main__':main()
