from pathlib import Path
import copy,json,time
import numpy as np, pandas as pd, torch
from torch import nn
ROOT=Path(__file__).resolve().parent
SEEDS=[11,22]; D=4; K=8; WIDTH=48

def make_worlds(seed=23001,n=600):
    rng=np.random.default_rng(seed); Ms=[];bs=[]
    for _ in range(n):
        A=rng.normal(0,.45,(D,D)); A*=rng.random((D,D))<.60
        ev=max(abs(np.linalg.eigvals(A)).max(),1e-6); A=A/ev*rng.uniform(.72,.90)
        row=np.max(np.sum(np.abs(A),axis=1))
        if row>.95:A=A*(.95/row)
        b=rng.uniform(-.35,.35,D); Ms.append(A.astype('float32'));bs.append(b.astype('float32'))
    return np.stack(Ms),np.stack(bs)

def equilibrium(M,b,u): return np.linalg.solve(np.eye(D,dtype=np.float32)-M,b+u)
def rollout_np(M,b,x0,h):
    x=x0.astype('float32').copy()
    for _ in range(h): x=M@x+b
    return x

def make_context_bank(Ms,bs,seed=23002,n_event=16):
    rng=np.random.default_rng(seed);eq=[];tm=[]
    for M,b in zip(Ms,bs):
        e=[];t=[]
        for _ in range(n_event):
            u=rng.uniform(-1,1,D).astype('float32'); y=equilibrium(M,b,u).astype('float32');e.append(np.r_[u,y].astype('float32'))
            x=rng.uniform(-1.3,1.3,D).astype('float32'); z=(M@x+b).astype('float32');t.append(np.r_[x,z].astype('float32'))
        eq.append(e);tm.append(t)
    return np.asarray(eq,np.float32),np.asarray(tm,np.float32)

def constrain_M(M):
    den=torch.maximum(M.abs().sum(-1,keepdim=True)/.95,torch.ones_like(M[...,:1])); return M/den
class Block(nn.Module):
    def __init__(self,d=WIDTH,heads=4,ff=96):
        super().__init__();self.n1=nn.LayerNorm(d);self.a=nn.MultiheadAttention(d,heads,batch_first=True,dropout=0.);self.n2=nn.LayerNorm(d);self.ff=nn.Sequential(nn.Linear(d,ff),nn.GELU(),nn.Linear(ff,d))
    def forward(self,x):
        q=self.n1(x);z,_=self.a(q,q,q,need_weights=False);x=x+z;return x+self.ff(self.n2(x))
class WorldProgram(nn.Module):
    def __init__(self,K=K,d=WIDTH):
        super().__init__();self.K=K;self.ev=nn.Linear(8,d);self.ev_type=nn.Embedding(2,d);self.cand=nn.Linear(D*D+D+1,d);self.seed=nn.Parameter(torch.randn(K,d)*.02);self.typ=nn.Embedding(2,d);self.blocks=nn.ModuleList([Block(d) for _ in range(3)]);self.out=nn.Linear(d,D*D+D+1);self.mix_gain=nn.Parameter(torch.tensor(1.2))
    def evidence_tokens(self,ctx,kind):return self.ev(ctx)+self.ev_type(kind)+self.typ.weight[0]
    def candidate_tokens(self,M,b,lg):
        f=torch.cat([M.reshape(len(M),self.K,-1),b,lg[:,:,None]],-1);return self.cand(f)+self.seed[None]+self.typ.weight[1]
    def transition(self,ev,M,b,lg):
        h=torch.cat([self.candidate_tokens(M,b,lg),ev],1)
        for block in self.blocks:h=block(h)
        o=self.out(h[:,:self.K]);Mp=constrain_M(torch.tanh(o[:,:,:D*D].reshape(len(M),self.K,D,D)));bp=.75*torch.tanh(o[:,:,D*D:D*D+D]);lp=o[:,:,-1]
        g=torch.sigmoid(self.mix_gain);Mn=constrain_M((1-g)*M+g*Mp);bn=(1-g)*b+g*bp;ln=(1-g)*lg+g*lp;ln=ln-ln.mean(-1,keepdim=True);return Mn,bn,ln
    def form_world(self,ctx,kind,steps=4,start_state=None,trace=False):
        n=len(ctx);ev=self.evidence_tokens(ctx,kind)
        if start_state is None:M=torch.zeros(n,self.K,D,D,device=ctx.device);b=torch.zeros(n,self.K,D,device=ctx.device);lg=torch.zeros(n,self.K,device=ctx.device)
        else:M,b,lg=start_state
        Ms=[];bs=[];ls=[]
        for _ in range(steps):M,b,lg=self.transition(ev,M,b,lg);Ms.append(M);bs.append(b);ls.append(lg)
        if trace:return M,b,lg,{'M':torch.stack(Ms,1),'b':torch.stack(bs,1),'logits':torch.stack(ls,1)}
        return M,b,lg
class DirectAttention(nn.Module):
    def __init__(self,d=WIDTH):
        super().__init__();self.ev=nn.Linear(8,d);self.ev_type=nn.Embedding(2,d);self.blocks=nn.ModuleList([Block(d) for _ in range(3)]);self.q=nn.Sequential(nn.Linear(2+D+2,d),nn.GELU(),nn.Linear(d,d));self.head=nn.Sequential(nn.Linear(2*d,128),nn.GELU(),nn.Linear(128,128),nn.GELU(),nn.Linear(128,D))
    def forward(self,ctx,kind,qfeat):
        h=self.ev(ctx)+self.ev_type(kind)
        for b in self.blocks:h=b(h)
        return self.head(torch.cat([h.mean(1),self.q(qfeat)],-1))
def exec_eq(M,b,u):
    A=torch.eye(D,device=M.device,dtype=M.dtype)-M;rhs=b+u[:,None,:];return torch.linalg.solve(A,rhs[...,None]).squeeze(-1)
def exec_temp(M,b,x0,h):
    Bn,Kk=len(M),M.shape[1];x=x0[:,None,:].expand(Bn,Kk,D).clone();out=torch.zeros_like(x)
    for t in range(1,int(h.max())+1):
        x=torch.einsum('bkij,bkj->bki',M,x)+b;sel=h==t
        if sel.any():out[sel]=x[sel]
    return out
def expected(pred,lg):return (pred*lg.softmax(-1)[:,:,None]).sum(1)

def sample_batch(rng,ids,Ms,bs,eqbank,tmbank,batch=96,nctx=None,mode='train',presentation=None):
    wi=rng.choice(ids,size=batch,replace=True);fam=rng.integers(0,2,size=batch) if presentation is None else np.full(batch,presentation)
    if nctx is None:nctx=int(rng.integers(4,9))
    ctx=np.zeros((batch,nctx,8),np.float32);kind=np.zeros((batch,nctx),np.int64);qfeat=np.zeros((batch,2+D+2),np.float32);truth=np.zeros((batch,D),np.float32)
    for i,(w,f) in enumerate(zip(wi,fam)):
        M=Ms[w];b=bs[w]
        if f==0:
            pick=rng.choice(len(eqbank[w]),size=nctx,replace=False);ctx[i]=eqbank[w,pick];kind[i]=0;ctx[i]=ctx[i][rng.permutation(nctx)]
            scale=1. if mode=='train' else 1.8;u=rng.uniform(-scale,scale,D).astype('float32');truth[i]=equilibrium(M,b,u);qfeat[i,0]=1;qfeat[i,2:2+D]=u
        else:
            pick=rng.choice(len(tmbank[w]),size=nctx,replace=False);ctx[i]=tmbank[w,pick];kind[i]=1;ctx[i]=ctx[i][rng.permutation(nctx)]
            x0=rng.uniform(-1.3,1.3,D).astype('float32');h=int(rng.integers(1,5)) if mode=='train' else int(rng.choice([1,2,4,8,16,32]));truth[i]=rollout_np(M,b,x0,h);qfeat[i,1]=1;qfeat[i,2:2+D]=x0;qfeat[i,-2]=h/4.
    return torch.tensor(ctx),torch.tensor(kind),torch.tensor(qfeat),torch.tensor(truth),wi

def world_predict(model,ctx,kind,qfeat,steps=4):
    M,b,lg=model.form_world(ctx,kind,steps=steps);is_eq=qfeat[:,0]>.5;pred=torch.zeros(len(ctx),K,D)
    if is_eq.any():pred[is_eq]=exec_eq(M[is_eq],b[is_eq],qfeat[is_eq,2:2+D])
    if (~is_eq).any():
        h=torch.clamp(torch.round(qfeat[~is_eq,-2]*4).long(),1,128);pred[~is_eq]=exec_temp(M[~is_eq],b[~is_eq],qfeat[~is_eq,2:2+D],h)
    return expected(pred,lg),(M,b,lg)

def build_eval(Ms,bs,eqbank,tmbank,ids,seed=2399):
    rng=np.random.default_rng(seed);rows=[]
    for w in ids:
        eq8=eqbank[w,:8][rng.permutation(8)];tm8=tmbank[w,:8][rng.permutation(8)];mixed=np.concatenate([eqbank[w,:4],tmbank[w,:4]],0);mk=np.r_[np.zeros(4,int),np.ones(4,int)];oo=rng.permutation(8);mixed=mixed[oo];mk=mk[oo]
        for pres,c,k in [('eq',eq8,np.zeros(8,int)),('mixed',mixed,mk)]:
            for regime,scale in [('eq_in',1.),('eq_extrap',1.8)]:
                for rep in range(3):
                    u=rng.uniform(-scale,scale,D).astype('float32');y=equilibrium(Ms[w],bs[w],u);q=np.zeros(2+D+2,np.float32);q[0]=1;q[2:2+D]=u;rows.append((w,pres,regime,0,rep,c,k,q,y))
        for pres,c,k in [('temp',tm8,np.ones(8,int)),('mixed',mixed,mk)]:
            for h in [1,2,4,8,16,32]:
                for rep in range(3):
                    x0=rng.uniform(-1.3,1.3,D).astype('float32');y=rollout_np(Ms[w],bs[w],x0,h);q=np.zeros(2+D+2,np.float32);q[1]=1;q[2:2+D]=x0;q[-2]=h/4.;rows.append((w,pres,'temp',h,rep,c,k,q,y))
    return rows

def eval_models(world,direct,rows,permute=False):
    out=[]
    for st in range(0,len(rows),256):
        ch=rows[st:st+256];C=[];KIND=[];Q=[];Y=[]
        for r in ch:
            c=r[5].copy();k=r[6].copy()
            if permute:c=c[::-1].copy();k=k[::-1].copy()
            C.append(c);KIND.append(k);Q.append(r[7]);Y.append(r[8])
        C=torch.tensor(np.stack(C));KIND=torch.tensor(np.stack(KIND));Q=torch.tensor(np.stack(Q));Y=torch.tensor(np.stack(Y))
        with torch.no_grad():wp,_=world_predict(world,C,KIND,Q);dp=direct(C,KIND,Q)
        for j,r in enumerate(ch):
            for name,p in [('world',wp[j]),('direct',dp[j])]:out.append({'world_id':r[0],'presentation':r[1],'regime':r[2],'horizon':r[3],'rep':r[4],'model':name,'mse':float(((p-Y[j])**2).mean()),'pred0':float(p[0]),'truth0':float(Y[j,0])})
    return pd.DataFrame(out)

def mechanism_diag(world,Ms,bs,eqbank,tmbank,ids):
    rng=np.random.default_rng(23077);rec=[]
    for pres in ['eq','temp','mixed']:
        C=[];KI=[];TM=[];TB=[];ww=[]
        for w in ids:
            if pres=='eq':c=eqbank[w,:8].copy();k=np.zeros(8,int)
            elif pres=='temp':c=tmbank[w,:8].copy();k=np.ones(8,int)
            else:c=np.concatenate([eqbank[w,:4],tmbank[w,:4]],0);k=np.r_[np.zeros(4,int),np.ones(4,int)]
            o=rng.permutation(8);C.append(c[o]);KI.append(k[o]);TM.append(Ms[w]);TB.append(bs[w]);ww.append(w)
        with torch.no_grad():M,b,lg=world.form_world(torch.tensor(np.stack(C)),torch.tensor(np.stack(KI)),steps=4);wgt=lg.softmax(-1).numpy();mn=M.numpy();bn=b.numpy()
        tM=np.stack(TM);tb=np.stack(TB);dm=np.sqrt(((mn-tM[:,None])**2).mean((2,3)));db=np.sqrt(((bn-tb[:,None])**2).mean(2))
        for i,w in enumerate(ww):rec.append({'world_id':w,'presentation':pres,'weighted_M_dist':float((wgt[i]*dm[i]).sum()),'best_M_dist':float(dm[i].min()),'weighted_b_dist':float((wgt[i]*db[i]).sum())})
    return pd.DataFrame(rec)

def train(seed,Ms,bs,eqbank,tmbank,train_ids,dev_ids,test_ids,updates=700):
    torch.manual_seed(seed);rng=np.random.default_rng(seed+23000);world=WorldProgram();direct=DirectAttention();ow=torch.optim.Adam(world.parameters(),lr=.0015);od=torch.optim.Adam(direct.parameters(),lr=.0015)
    bestw=bestd=1e9;sw=sd=None;logs=[];t0=time.time()
    for step in range(1,updates+1):
        ctx,kind,q,y,_=sample_batch(rng,train_ids,Ms,bs,eqbank,tmbank,batch=96,nctx=None,mode='train')
        ow.zero_grad();wp,_=world_predict(world,ctx,kind,q,steps=int(rng.integers(3,7)));lw=((wp-y)**2).mean();lw.backward();torch.nn.utils.clip_grad_norm_(world.parameters(),5);ow.step()
        od.zero_grad();dp=direct(ctx,kind,q);ld=((dp-y)**2).mean();ld.backward();torch.nn.utils.clip_grad_norm_(direct.parameters(),5);od.step()
        if step%50==0:
            vb=sample_batch(np.random.default_rng(9000+step),dev_ids,Ms,bs,eqbank,tmbank,batch=256,nctx=8,mode='train');vctx,vkind,vq,vy,_=vb
            with torch.no_grad():vwp,_=world_predict(world,vctx,vkind,vq,steps=4);vdp=direct(vctx,vkind,vq);vlw=float(((vwp-vy)**2).mean());vld=float(((vdp-vy)**2).mean())
            logs.append({'step':step,'train_world_mse':float(lw.detach()),'train_direct_mse':float(ld.detach()),'dev_world_mse':vlw,'dev_direct_mse':vld})
            if vlw<bestw:bestw=vlw;sw=copy.deepcopy(world.state_dict());selw=step
            if vld<bestd:bestd=vld;sd=copy.deepcopy(direct.state_dict());seld=step
            print(seed,step,vlw,vld,flush=True)
    world.load_state_dict(sw);direct.load_state_dict(sd);world.eval();direct.eval();rows=build_eval(Ms,bs,eqbank,tmbank,test_ids,seed=2399);detail=eval_models(world,direct,rows);detail['seed']=seed
    pdetail=eval_models(world,direct,rows[:800],permute=True);base=detail.iloc[:len(pdetail)].copy();perm_delta=float(np.max(np.abs(pdetail.mse.to_numpy()-base.mse.to_numpy())))
    sample=rows[:128];C=torch.tensor(np.stack([r[5] for r in sample]));KI=torch.tensor(np.stack([r[6] for r in sample]))
    with torch.no_grad():
        _,_,_,tr=world.form_world(C,KI,steps=2,trace=True);st=(tr['M'][:,-1].clone(),tr['b'][:,-1].clone(),tr['logits'][:,-1].clone());Mr,br,lr=world.form_world(C,KI,steps=2,start_state=st);M4,b4,l4=world.form_world(C,KI,steps=4);replay=max(float((Mr-M4).abs().max()),float((br-b4).abs().max()),float((lr-l4).abs().max()))
    mech=mechanism_diag(world,Ms,bs,eqbank,tmbank,test_ids);mech['seed']=seed
    C=torch.tensor(np.stack([np.concatenate([eqbank[w,:4],tmbank[w,:4]],0) for w in test_ids[:100]]));KI=torch.tensor(np.stack([np.r_[np.zeros(4,int),np.ones(4,int)] for _ in test_ids[:100]]));curve=[];state=None;prev=None
    with torch.no_grad():
        for s in range(1,21):
            M,b,l=world.form_world(C,KI,steps=1,start_state=state);r=np.nan if prev is None else float((M-prev).square().mean().sqrt());curve.append({'seed':seed,'step':s,'M_step_rms':r});state=(M,b,l);prev=M.clone()
    torch.save({'world':sw,'direct':sd,'seed':seed,'selected_world_step':selw,'selected_direct_step':seld},ROOT/'models'/f'cg023_{seed}.pt');(ROOT/'models'/f'cg023_{seed}_training.json').write_text(json.dumps(logs,indent=2))
    metrics={'seed':seed,'world_params':sum(p.numel() for p in world.parameters()),'direct_params':sum(p.numel() for p in direct.parameters()),'selected_world_step':selw,'selected_direct_step':seld,'dev_world_mse':bestw,'dev_direct_mse':bestd,'permutation_mse_max_delta':perm_delta,'state_replay_max_abs':replay,'seconds':time.time()-t0}
    return metrics,detail,mech,pd.DataFrame(curve)

def main():
    torch.set_num_threads(4);Ms,bs=make_worlds();eqbank,tmbank=make_context_bank(Ms,bs);np.savez_compressed(ROOT/'world_data.npz',M=Ms,b=bs,eqbank=eqbank,tmbank=tmbank,split=np.r_[np.zeros(400,int),np.ones(100,int),np.full(100,2,int)])
    train_ids=np.arange(400);dev_ids=np.arange(400,500);test_ids=np.arange(500,600);mets=[];dets=[];mechs=[];curves=[]
    for seed in SEEDS:
        m,d,g,c=train(seed,Ms,bs,eqbank,tmbank,train_ids,dev_ids,test_ids);mets.append(m);dets.append(d);mechs.append(g);curves.append(c);pd.DataFrame(mets).to_csv(ROOT/'results.csv',index=False);pd.concat(dets,ignore_index=True).to_csv(ROOT/'eval_detail.csv',index=False);pd.concat(mechs,ignore_index=True).to_csv(ROOT/'mechanism_diagnostics.csv',index=False);pd.concat(curves,ignore_index=True).to_csv(ROOT/'world_rollout.csv',index=False);print(json.dumps(m),flush=True)
    print('COMPLETE',flush=True)
if __name__=='__main__':main()
