import math, random, copy, json, os, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pack_padded_sequence

LANGS=['en','zh','ja','es','py','js']; L2I={x:i for i,x in enumerate(LANGS)}

def signed_expr_tokens(a,b,lang):
    toks=[str(a),'*','x']
    if b>0: toks += ['+',str(b)]
    elif b<0: toks += ['-',str(abs(b))]
    return toks

def render_tokens(s,lang):
    cmp_,t,a,b,c,d=s; e1=signed_expr_tokens(a,b,lang); e2=signed_expr_tokens(c,d,lang)
    if lang=='en': return ['if','x','is','greater_than' if cmp_=='>' else 'less_than',str(t),',','return']+e1+[';','otherwise','return']+e2+['.']
    if lang=='zh': return ['如果','x','大于' if cmp_=='>' else '小于',str(t),'，','则','返回']+e1+['；','否则','返回']+e2+['。']
    if lang=='ja': return ['もし','x','が',str(t),'より大きい' if cmp_=='>' else 'より小さい','なら','返す']+e1+['；','それ以外','返す']+e2+['。']
    if lang=='es': return ['si','x','es','mayor_que' if cmp_=='>' else 'menor_que',str(t),',','devuelve']+e1+[';','si_no','devuelve']+e2+['.']
    if lang=='py': return ['def','f','(','x',')',':','if','x',cmp_,str(t),':','return']+e1+['NEWLINE','return']+e2
    if lang=='js': return ['function','f','(','x',')','{','if','(','x',cmp_,str(t),')','return']+e1+[';','return']+e2+[';','}']

def render_text(s,lang):
    toks=render_tokens(s,lang)
    if lang=='py': return ' '.join(toks).replace(' NEWLINE ','\n')
    return ' '.join(toks)

def gen_scenes(n,seed):
    rng=random.Random(seed); A=[-4,-3,-2,2,3,4]; B=[-5,-3,-1,0,1,3,5]; T=[-3,-2,-1,0,1,2,3]
    seen=set(); out=[]
    while len(out)<n:
        s=(rng.choice(['>','<']),rng.choice(T),rng.choice(A),rng.choice(B),rng.choice(A),rng.choice(B))
        if s not in seen: seen.add(s); out.append(s)
    return out

ALL_SCENES=gen_scenes(1200,777)
all_tokens=set()
for s in ALL_SCENES[:1000]:
    for l in LANGS: all_tokens.update(render_tokens(s,l))
SPECIAL=['<PAD>','<BOS>','<EOS>']
ITOS=SPECIAL+sorted(all_tokens); STOI={t:i for i,t in enumerate(ITOS)}
PAD,BOS,EOS=0,1,2; VOCAB=len(ITOS)

def encode(s,lang): return [STOI[t] for t in render_tokens(s,lang)]+[EOS]
def pad(seqs,device):
    lens=torch.tensor([len(x) for x in seqs],dtype=torch.long)
    m=max(map(len,seqs)); x=torch.full((len(seqs),m),PAD,dtype=torch.long,device=device)
    for i,s in enumerate(seqs): x[i,:len(s)]=torch.tensor(s,device=device)
    return x,lens

class M(nn.Module):
    def __init__(self,emb=32,eh=32,dh=48,core=16,ld=6):
        super().__init__(); self.emb=nn.Embedding(VOCAB,emb,padding_idx=PAD); self.lang=nn.Embedding(6,ld)
        self.enc=nn.GRU(emb,eh,batch_first=True,bidirectional=True)
        self.pre=nn.Linear(2*eh+ld,core); self.core=nn.Linear(core,core)
        self.init=nn.Linear(core+ld,dh); self.dec=nn.GRU(emb+ld+core,dh,batch_first=True); self.out=nn.Linear(dh+core,VOCAB)
    def encode(self,x,lens,sl):
        p=pack_padded_sequence(self.emb(x),lens.cpu(),batch_first=True,enforce_sorted=False); _,h=self.enc(p)
        h=torch.cat([h[-2],h[-1],self.lang(sl)],-1); z0=torch.tanh(self.pre(h)); return torch.tanh(z0+self.core(z0))
    def teach(self,z,tl,y):
        B,T=y.shape; inp=torch.full_like(y,PAD); inp[:,0]=BOS; inp[:,1:]=y[:,:-1]
        le=self.lang(tl); h=torch.tanh(self.init(torch.cat([z,le],-1))).unsqueeze(0)
        em=self.emb(inp); zc=z[:,None,:].expand(B,T,-1); o,_=self.dec(torch.cat([em,le[:,None,:].expand(B,T,-1),zc],-1),h); return self.out(torch.cat([o,zc],-1))
    @torch.no_grad()
    def gen(self,z,tl,maxlen=40):
        B=z.shape[0]; le=self.lang(tl); h=torch.tanh(self.init(torch.cat([z,le],-1))).unsqueeze(0); cur=torch.full((B,1),BOS,dtype=torch.long,device=z.device)
        outs=[[] for _ in range(B)]; done=[False]*B
        for _ in range(maxlen):
            zc=z[:,None,:]; o,h=self.dec(torch.cat([self.emb(cur),le[:,None,:],zc],-1),h); nxt=self.out(torch.cat([o[:,-1],z],-1)).argmax(-1); cur=nxt[:,None]
            for i,t in enumerate(nxt.tolist()):
                if not done[i]:
                    if t==EOS: done[i]=True
                    elif t!=PAD: outs[i].append(t)
            if all(done): break
        return outs

def makebatch(scenes,B,rng,mode,device):
    idx=[rng.randrange(len(scenes)) for _ in range(B)]; sl=[rng.randrange(6) for _ in range(B)]; tl=list(sl) if mode=='self' else [rng.randrange(6) for _ in range(B)]; tidx=list(idx)
    if mode=='shuffle':
        shifted=idx[1:]+idx[:1]
        for i in range(B):
            if sl[i]!=tl[i]: tidx[i]=shifted[i]
    x,lens=pad([encode(scenes[j],LANGS[sl[i]]) for i,j in enumerate(idx)],device)
    y,_=pad([encode(scenes[tidx[i]],LANGS[tl[i]]) for i in range(B)],device)
    return x,lens,torch.tensor(sl,device=device),y,torch.tensor(tl,device=device)

SEM_TOKENS=set([str(i) for i in range(-5,6)] + ['>','<','+','-','greater_than','less_than','大于','小于','より大きい','より小さい','mayor_que','menor_que'])
SEM_IDS=set(STOI[t] for t in SEM_TOKENS if t in STOI)
def loss(log,y):
    flat=F.cross_entropy(log.reshape(-1,VOCAB),y.reshape(-1),ignore_index=PAD,reduction='none').reshape_as(y)
    mask=(y!=PAD)
    w=torch.full_like(flat,0.35)
    sem=torch.zeros_like(mask)
    for tid in SEM_IDS: sem |= (y==tid)
    w[sem]=2.5
    return (flat*w*mask).sum()/(w*mask).sum().clamp_min(1)


def train(model,scenes,steps,seed,mode,lr=4e-3,B=96,trace=100):
    rng=random.Random(seed); opt=torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=1e-4); H=[]
    for st in range(steps):
        x,le,sl,y,tl=makebatch(scenes,B,rng,mode,DEVICE); z=model.encode(x,le,sl); lo=model.teach(z,tl,y); L=loss(lo,y)
        opt.zero_grad(); L.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step()
        if st%trace==0 or st==steps-1: H.append({'step':st+1,'loss':float(L.detach()),'core_norm':float(model.core.weight.detach().norm())})
    return H

@torch.no_grad()
def allZ(model,scenes):
    arr=[]
    for li,l in enumerate(LANGS):
        x,le=pad([encode(s,l) for s in scenes],DEVICE); sl=torch.full((len(scenes),),li,dtype=torch.long,device=DEVICE); arr.append(model.encode(x,le,sl).cpu().numpy())
    return np.stack(arr,2) # n x 16 x 6

def zmetrics(Z,scenes):
    n,d,v=Z.shape; Xall=Z.transpose(0,2,1).reshape(-1,d); scale=np.std(Xall,0).mean()+1e-8; ds=[]; cs=[]
    for i in range(n):
        for a in range(v):
            for b in range(a+1,v):
                x=Z[i,:,a]; y=Z[i,:,b]; ds.append(np.linalg.norm(x-y)/math.sqrt(d)/scale); cs.append(np.dot(x,y)/(np.linalg.norm(x)*np.linalg.norm(y)+1e-8))
    Y=[]
    for s in scenes:
        cmp_,t,a,b,c,e=s
        for _ in range(6): Y.append([1 if cmp_=='>' else -1,t,a,b,c,e])
    Y=np.array(Y,float); cut=int(.7*n); tr=np.arange(cut*6); te=np.arange(cut*6,n*6)
    Xtr=np.c_[np.ones(len(tr)),Xall[tr]]; Xte=np.c_[np.ones(len(te)),Xall[te]]; W=np.linalg.pinv(Xtr)@Y[tr]; P=Xte@W
    r2=1-((Y[te]-P)**2).sum(0)/(((Y[te]-Y[te].mean(0))**2).sum(0)+1e-9)
    # singular spectrum of 16x6 same-scene matrix after centering columns; measure residual view spread energy
    svals=[]
    for i in range(n):
        C=Z[i]-Z[i].mean(1,keepdims=True); sv=np.linalg.svd(C,compute_uv=False); svals.append(sv)
    sv=np.mean(np.array(svals),0)
    return {'same_scene_dist':float(np.mean(ds)),'same_scene_cos':float(np.mean(cs)),'probe_r2_mean':float(r2.mean()),'probe_r2_each':r2.tolist(),'mean_centered_singular_values':sv.tolist()}

@torch.no_grad()
def pairs(model,scenes):
    ce=np.zeros((6,6)); ac=np.zeros((6,6)); sac=np.zeros((6,6)); scenes=scenes[:120]
    for si,sla in enumerate(LANGS):
        x,le=pad([encode(s,sla) for s in scenes],DEVICE); sl=torch.full((len(scenes),),si,dtype=torch.long,device=DEVICE); z=model.encode(x,le,sl)
        for ti,tla in enumerate(LANGS):
            y,_=pad([encode(s,tla) for s in scenes],DEVICE); tl=torch.full((len(scenes),),ti,dtype=torch.long,device=DEVICE); lo=model.teach(z,tl,y); ce[si,ti]=float(loss(lo,y)); pr=lo.argmax(-1); mask=y!=PAD; ac[si,ti]=float((pr[mask]==y[mask]).float().mean())
            sm=torch.zeros_like(mask)
            for tid in SEM_IDS: sm |= (y==tid)
            sac[si,ti]=float((pr[sm]==y[sm]).float().mean()) if sm.any() else float('nan')
    off=~np.eye(6,dtype=bool)
    return {'self_ce':float(np.diag(ce).mean()),'cross_ce':float(ce[off].mean()),'self_tok_acc':float(np.diag(ac).mean()),'cross_tok_acc':float(ac[off].mean()),'self_sem_acc':float(np.diag(sac).mean()),'cross_sem_acc':float(sac[off].mean()),'ce_matrix':ce.tolist(),'tok_acc_matrix':ac.tolist(),'sem_acc_matrix':sac.tolist()}

@torch.no_grad()
def greedy(model,scenes,n=20):
    exact=[]; semexec=[]; examples=[]
    # semantic execution proxy: generated token sequence exactly identifies canonical target; also parse parameters if canonical prefix intact is omitted for now
    for s in scenes[:n]:
        for si,sla in enumerate(LANGS):
            x,le=pad([encode(s,sla)],DEVICE); z=model.encode(x,le,torch.tensor([si],device=DEVICE))
            for ti,tla in enumerate(LANGS):
                if ti==si: continue
                out=model.gen(z,torch.tensor([ti],device=DEVICE))[0]; tgt=encode(s,tla)[:-1]; ex=(out==tgt); exact.append(ex)
                if len(examples)<8:
                    txt=' '.join(ITOS[t] for t in out); examples.append({'src':render_text(s,sla),'src_lang':sla,'tgt_lang':tla,'target':render_text(s,tla),'generated_tokens':txt,'exact':ex})
    return {'cross_exact':float(np.mean(exact)),'examples':examples}

def delta(a,b):
    grp={'encoder':['emb.','lang.','enc.','pre.'],'core':['core.'],'decoder':['init.','dec.','out.']}; o={}
    for g,ps in grp.items():
        ss=0
        for k,v in b.items():
            if any(k.startswith(p) for p in ps): ss+=float(((v-a[k]).float()**2).sum())
        o[g]=math.sqrt(ss)
    return o

DEVICE=torch.device('cpu'); torch.set_num_threads(min(8,os.cpu_count() or 1))

def run(seed=0,selfsteps=350,bindsteps=650):
    train_s=ALL_SCENES[:800]; test_s=ALL_SCENES[1000:1200]
    torch.manual_seed(seed); random.seed(seed); np.random.seed(seed); m=M().to(DEVICE)
    hs=train(m,train_s,selfsteps,seed+1,'self'); st={k:v.detach().cpu().clone() for k,v in m.state_dict().items()}
    Rself={**zmetrics(allZ(m,test_s),test_s),**pairs(m,test_s),**greedy(m,test_s,10)}
    p=copy.deepcopy(m); a={k:v.detach().cpu().clone() for k,v in p.state_dict().items()}; train(p,train_s,1,seed+99,'bind',B=96,trace=1); b={k:v.detach().cpu().clone() for k,v in p.state_dict().items()}; fd=delta(a,b)
    hb=train(m,train_s,bindsteps,seed+2,'bind'); Rbind={**zmetrics(allZ(m,test_s),test_s),**pairs(m,test_s),**greedy(m,test_s,10)}
    sh=M().to(DEVICE); sh.load_state_dict(st); hh=train(sh,train_s,bindsteps,seed+3,'shuffle'); Rsh={**zmetrics(allZ(sh,test_s),test_s),**pairs(sh,test_s),**greedy(sh,test_s,10)}
    return {'seed':seed,'vocab':ITOS,'self':Rself,'bind':Rbind,'shuffle':Rsh,'first_binding_delta':fd,'trace_self':hs,'trace_bind':hb,'trace_shuffle':hh},st,{k:v.detach().cpu().clone() for k,v in m.state_dict().items()}

if __name__=='__main__':
    t=time.time(); R,S,B=run(0); json.dump(R,open('/mnt/data/IC003_fast_seed0.json','w'),ensure_ascii=False,indent=2); torch.save({'self':S,'bind':B},'/mnt/data/IC003_fast_seed0.pt')
    keys=['cross_ce','cross_tok_acc','same_scene_dist','same_scene_cos','probe_r2_mean','cross_exact']
    print('elapsed',time.time()-t,'vocab',VOCAB)
    for c in ['self','bind','shuffle']: print(c,{k:R[c][k] for k in keys})
    print('first_delta',R['first_binding_delta'])
