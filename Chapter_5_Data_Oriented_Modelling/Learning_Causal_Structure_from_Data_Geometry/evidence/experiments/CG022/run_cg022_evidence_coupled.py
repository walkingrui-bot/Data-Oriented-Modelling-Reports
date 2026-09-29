from pathlib import Path
import copy,json,time
import numpy as np,pandas as pd,torch
import run_cg022_engineered_world as core
import run_cg022_balanced as bal
ROOT=Path(__file__).resolve().parent
SEEDS=[11,22]

def fit(seed,train,dev,test,steps=500):
 torch.manual_seed(seed);rng=np.random.default_rng(seed+2422);m=core.WorldProgram(core.K);opt=torch.optim.Adam(m.parameters(),lr=.0015)
 x,y,tb=train;vx,vy,vtb=dev;tx,ty,ttb,group,support=test;best=1e9;state=None;logs=[];t0=time.time()
 for step in range(1,steps+1):
  ix=rng.integers(len(x),size=64);xb=x[ix];yb=y[ix];tbb=tb[ix];horizon=int(rng.integers(3,7));picks=rng.choice(len(core.TRAIN_SPECS),size=6,replace=False);specs=[core.TRAIN_SPECS[j] for j in picks]
  opt.zero_grad();B,lg=m.form_world(xb,steps=horizon);orig=bal.query_nll_vec(B,lg,xb,yb).mean();bank=core.bank_loss(B,lg,tbb,specs)
  sm=xb[:,12:15].sum(-1)>0;ev=torch.tensor(0.,dtype=orig.dtype);opgain=torch.tensor(0.,dtype=orig.dtype)
  if sm.any():
   postobs=bal.support_obs_nll(B[sm],lg[sm],xb[sm]).mean();xm=xb.clone();xm[:,9:15]=0;Bm,lm=m.form_world(xm,steps=horizon)
   postbank=core.bank_loss(B[sm],lg[sm],tbb[sm],specs);maskbank=core.bank_loss(Bm[sm],lm[sm],tbb[sm],specs)
   ev=postobs;opgain=torch.relu(postbank-maskbank+0.05)
  loss=.35*orig+.35*bank+.10*ev+.20*opgain;loss.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),5);opt.step()
  if step%50==0:
   with torch.no_grad():
    Bv,lv=m.form_world(vx,steps=4);vo=bal.query_nll_vec(Bv,lv,vx,vy).mean();vb=core.bank_loss(Bv,lv,vtb,core.TRAIN_SPECS)
    svm=vx[:,12:15].sum(-1)>0;xvm=vx.clone();xvm[:,9:15]=0;Bvm,lvm=m.form_world(xvm,steps=4)
    post=core.bank_loss(Bv[svm],lv[svm],vtb[svm],core.TRAIN_SPECS);masked=core.bank_loss(Bvm[svm],lvm[svm],vtb[svm],core.TRAIN_SPECS);gp=torch.relu(post-masked+0.02);score=float(.45*vo+.45*vb+.10*gp)
   logs.append({'step':step,'train_total':float(loss.detach()),'train_original':float(orig.detach()),'train_bank':float(bank.detach()),'train_evidence_obs':float(ev.detach()),'train_operator_gain_penalty':float(opgain.detach()),'dev_original_nll':float(vo),'dev_operator_bank_nll':float(vb),'dev_operator_gain_penalty':float(gp),'dev_score':score,'horizon':horizon})
   if score<best:best=score;state=copy.deepcopy(m.state_dict());sel=step
 m.load_state_dict(state);m.eval();metrics,detail,tr=core.evaluate(m,tx,ty,ttb,group,support,4)
 d=detail[detail.bank=='heldout_bank'].groupby(['group','support']).nll.mean().unstack();metrics['heldout_support_improvement']=float((d[0]-d[1]).mean())
 with torch.no_grad():
  Bf,lf=m.form_world(tx,steps=4);xm=tx.clone();xm[:,9:15]=0;Bm,lm=m.form_world(xm,steps=4);sm=torch.tensor(support.astype(bool));metrics['support_observation_nll_gain']=float((bal.support_obs_nll(Bm[sm],lm[sm],tx[sm])-bal.support_obs_nll(Bf[sm],lf[sm],tx[sm])).mean())
  metrics['support_operator_bank_gain']=float(core.bank_loss(Bm[sm],lm[sm],ttb[sm],core.HELD_SPECS)-core.bank_loss(Bf[sm],lf[sm],ttb[sm],core.HELD_SPECS))
  _,_,a=m.form_world(tx,steps=2,trace=True);st=(a['B'][:,-1].clone(),a['logits'][:,-1].clone());Br,Lr=m.form_world(tx,steps=2,start_state=st,reveal_step=1);B4,L4=m.form_world(tx,steps=4);metrics['state_replay_max_abs']=float(max((Br-B4).abs().max(),(Lr-L4).abs().max()))
 # wrong support transplant downstream effect
 donor=np.full(len(tx),-1,int)
 for g in np.unique(group):
  ids=np.flatnonzero((group==g)&(support==1))
  if len(ids)==3:
   for j,i in enumerate(ids):donor[i]=ids[(j+1)%3]
 ids=np.flatnonzero(donor>=0);ds=donor[ids];xs=tx.clone();xs[ids,9:15]=tx[ds,9:15]
 with torch.no_grad():
  Bw,lw=m.form_world(xs,steps=4);basev=bal.query_nll_vec(Bf[ids],lf[ids],tx[ids],ty[ids]);wrongown=bal.query_nll_vec(Bw[ids],lw[ids],xs[ids],ty[ids]);wrongdon=bal.query_nll_vec(Bw[ids],lw[ids],xs[ids],ty[ds])
 metrics['wrong_support_own_degradation']=float((wrongown-basev).mean());metrics['wrong_support_donor_preferred']=float((wrongdon<wrongown).float().mean())
 # rollout
 curves=[];xc=tx[:200];tbc=ttb[:200];B=None;lg=None;prev=None
 with torch.no_grad():
  for h in range(1,21):
   B,lg=m.form_world(xc,steps=1,start_state=None if h==1 else (B,lg),reveal_step=(99 if h<3 else 1));curves.append({'seed':seed,'variant':'evidence_coupled','step':h,'heldout_bank_nll':float(core.bank_loss(B,lg,tbc,core.HELD_SPECS)),'B_step_rms':np.nan if prev is None else float((B-prev).square().mean().sqrt())});prev=B.clone()
 torch.save({'state_dict':state,'seed':seed,'selected_step':sel,'K':core.K},ROOT/'models'/f'evidence_coupled_{seed}.pt');(ROOT/'models'/f'evidence_coupled_{seed}_training.json').write_text(json.dumps(logs,indent=2));np.savez_compressed(ROOT/'predictions'/f'evidence_coupled_{seed}.npz',B=tr['B'].numpy(),logits=tr['logits'].numpy())
 return {'seed':seed,'variant':'evidence_coupled','parameters':sum(p.numel() for p in m.parameters()),'selected_step':sel,'dev_score':best,'seconds':time.time()-t0,**metrics},detail,pd.DataFrame(curves)

def main():
 torch.set_num_threads(4);z=np.load(core.DATA);spl=[]
 for s in range(3):
  ix=z['split']==s;spl.append((torch.tensor(z['x'][ix],dtype=torch.float32),torch.tensor(z['y'][ix],dtype=torch.float32),torch.tensor(z['true_B'][ix],dtype=torch.float32)))
 ix=z['split']==2;test=(*spl[2],z['group'][ix],z['support'][ix]);res=[];det=[];cur=[]
 for seed in SEEDS:
  r,d,c=fit(seed,spl[0],spl[1],test);res.append(r);d['seed']=seed;d['variant']='evidence_coupled';det.append(d);cur.append(c);print(json.dumps(r),flush=True);pd.DataFrame(res).to_csv(ROOT/'evidence_coupled_results.csv',index=False);pd.concat(det,ignore_index=True).to_csv(ROOT/'evidence_coupled_operator_detail.csv',index=False);pd.concat(cur,ignore_index=True).to_csv(ROOT/'evidence_coupled_rollout.csv',index=False)
 print('COMPLETE',flush=True)
if __name__=='__main__':main()
