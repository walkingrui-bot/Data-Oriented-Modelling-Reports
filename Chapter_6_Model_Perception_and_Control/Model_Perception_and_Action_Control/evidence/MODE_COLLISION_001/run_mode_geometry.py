import json, math, copy, os, random, time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances
from scipy import sparse
from scipy.sparse.linalg import svds

SEED=7
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
torch.set_num_threads(4)
PAIRS=json.load(open('mode_collision_pairs.json'))
# pair-grouped split: every 5th pair held out
train_pairs=[i for i in range(len(PAIRS)) if i%5!=0]
test_pairs=[i for i in range(len(PAIRS)) if i%5==0]

# label 0 = TEXT/request-for-info, label 1 = ACT/original executable request
samples=[]
for pi,(text,act) in enumerate(PAIRS):
    samples.append((pi,0,text)); samples.append((pi,1,act))

PAD=0; BOS=1; BYTE0=2; VOCAB=258; MAXLEN=128

def encode(s):
    raw=list(s.encode('utf-8'))
    b=raw if len(raw)<=MAXLEN-1 else raw[:80]+raw[-47:]
    ids=[BOS]+[x+BYTE0 for x in b]
    return ids

def batchify(items):
    n=len(items); x=torch.zeros(n,MAXLEN,dtype=torch.long); lens=torch.zeros(n,dtype=torch.long); y=torch.zeros(n,dtype=torch.long)
    for i,(_,lab,s) in enumerate(items):
        ids=encode(s); x[i,:len(ids)]=torch.tensor(ids); lens[i]=len(ids); y[i]=lab
    return x,lens,y
train_items=[s for s in samples if s[0] in train_pairs]
test_items=[s for s in samples if s[0] in test_pairs]
Xtr,Ltr,Ytr=batchify(train_items); Xte,Lte,Yte=batchify(test_items)

class TinyCausal(nn.Module):
    def __init__(self, d=24, layers=8, heads=4, ff=64):
        super().__init__(); self.d=d
        self.emb=nn.Embedding(VOCAB,d,padding_idx=PAD); self.pos=nn.Embedding(MAXLEN,d)
        base=nn.TransformerEncoderLayer(d,heads,ff,dropout=0.0,batch_first=True,norm_first=True,activation='gelu')
        self.layers=nn.ModuleList([copy.deepcopy(base) for _ in range(layers)])
        self.final=nn.LayerNorm(d); self.head=nn.Linear(d,2)
        self.register_buffer('causal', torch.triu(torch.full((MAXLEN,MAXLEN), float('-inf')), diagonal=1), persistent=False)
    def forward(self,x,lens,return_h=False):
        n,T=x.shape; pos=torch.arange(T,device=x.device)[None,:]
        h=self.emb(x)+self.pos(pos); hs=[h]
        pad=(x==PAD)
        for layer in self.layers:
            h=layer(h,src_mask=self.causal[:T,:T],src_key_padding_mask=pad,is_causal=True)
            hs.append(h)
        h=self.final(h)
        idx=(lens-1).clamp(min=0)
        last=h[torch.arange(n,device=x.device),idx]
        logits=self.head(last)
        if return_h:
            # final-normalize every layer for comparability, without changing dynamics
            normed=[self.final(z) for z in hs]
            return logits,normed
        return logits

def acc(model,x,l,y):
    model.eval();
    with torch.no_grad(): return (model(x,l).argmax(-1)==y).float().mean().item()

model=TinyCausal()
init_state=copy.deepcopy(model.state_dict())
opt=torch.optim.AdamW(model.parameters(),lr=2e-3,weight_decay=1e-3)
lossfn=nn.CrossEntropyLoss()
N=len(train_items); bs=28
hist=[]; t0=time.time()
for epoch in range(1,101):
    model.train(); order=torch.randperm(N); total=0
    for st in range(0,N,bs):
        ii=order[st:st+bs]
        opt.zero_grad(set_to_none=True); logits=model(Xtr[ii],Ltr[ii]); loss=lossfn(logits,Ytr[ii]); loss.backward();
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step(); total+=loss.item()*len(ii)
    if epoch==1 or epoch%10==0:
        a=acc(model,Xtr,Ltr,Ytr); v=acc(model,Xte,Lte,Yte); hist.append((epoch,total/N,a,v))
        if a>0.995 and epoch>=40: break
print('training',hist[-8:],'seconds',time.time()-t0)

# Helpers for layer geometry on pair-grouped held-out set.
def extract(model,x,l):
    model.eval()
    with torch.no_grad():
        logits,hs=model(x,l,True)
    last=[]; mean=[]; clouds=[]
    for h in hs:
        arr=h.cpu().numpy();
        lv=np.stack([arr[i,l[i]-1] for i in range(len(l))])
        mv=np.stack([arr[i,:l[i]].mean(0) for i in range(len(l))])
        cv=np.concatenate([arr[i,:l[i]] for i in range(len(l))],axis=0)
        if len(cv)>2500:
            rng=np.random.default_rng(0); cv=cv[rng.choice(len(cv),2500,replace=False)]
        last.append(lv); mean.append(mv); clouds.append(cv)
    return logits.cpu().numpy(),last,mean,clouds

def eranks(Z):
    Z=Z-Z.mean(0,keepdims=True)
    if min(Z.shape)<2: return (0,0,[])
    s=np.linalg.svd(Z,compute_uv=False)
    e=s*s; total=e.sum()+1e-12
    stable=total/(e.max()+1e-12)
    p=e/total; eff=float(np.exp(-(p[p>0]*np.log(p[p>0])).sum()))
    spec=(e/total)[:16]
    return float(stable),eff,spec

def geo(Z,y,trainZ=None,trainY=None,pair_ids=None):
    y=np.asarray(y); Z=np.asarray(Z,float)
    A=Z[y==0]; B=Z[y==1]
    Da=pairwise_distances(A); Db=pairwise_distances(B); Dab=pairwise_distances(A,B)
    wa=Da[np.triu_indices_from(Da,1)].mean() if len(A)>1 else np.nan
    wb=Db[np.triu_indices_from(Db,1)].mean() if len(B)>1 else np.nan
    within=np.nanmean([wa,wb]); between=Dab.mean(); ratio=between/(within+1e-12)
    mu0=A.mean(0); mu1=B.mean(0); diff=mu1-mu0
    var=((A-mu0)**2).sum()/max(1,len(A)-1)+((B-mu1)**2).sum()/max(1,len(B)-1)
    fisher=float((diff@diff)/(var+1e-12))
    # local cross-class mixing k=5
    D=pairwise_distances(Z); np.fill_diagonal(D,np.inf); k=min(5,len(Z)-1)
    nnidx=np.argpartition(D,k,axis=1)[:,:k]
    mix=float((y[nnidx]!=y[:,None]).mean())
    # nearest centroid using train states only when available
    probe=np.nan; cent=np.nan
    if trainZ is not None:
        clf=LogisticRegression(C=1.0,max_iter=1000,solver='liblinear').fit(trainZ,trainY)
        probe=float((clf.predict(Z)==y).mean())
        c0=trainZ[np.asarray(trainY)==0].mean(0); c1=trainZ[np.asarray(trainY)==1].mean(0)
        pred=(((Z-c1)**2).sum(1)<((Z-c0)**2).sum(1)).astype(int)
        cent=float((pred==y).mean())
    stable,eff,spec=eranks(Z)
    Zc=Z-Z.mean(0); pc=PCA(n_components=1).fit(Zc).components_[0]
    pc_align=float(abs(np.dot(pc,diff)/(np.linalg.norm(diff)+1e-12)))
    # paired displacement on held-out paired ordering (items are text/act alternating by pair)
    deltas=[]
    if pair_ids is not None:
        for pid in sorted(set(pair_ids)):
            inds=[i for i,p in enumerate(pair_ids) if p==pid]
            if len(inds)==2:
                i0=[i for i in inds if y[i]==0][0]; i1=[i for i in inds if y[i]==1][0]
                deltas.append(Z[i1]-Z[i0])
    if deltas:
        Dlt=np.stack(deltas); nd=Dlt/(np.linalg.norm(Dlt,axis=1,keepdims=True)+1e-12)
        C=nd@nd.T; tri=C[np.triu_indices_from(C,1)]
        delta_align=float(tri.mean()) if len(tri) else np.nan
        md=nd.mean(0); md/=np.linalg.norm(md)+1e-12
        sign=float(((Dlt@md)>0).mean())
        delta_norm=float(np.linalg.norm(Dlt,axis=1).mean())
    else: delta_align=sign=delta_norm=np.nan
    return dict(within_distance=within,between_distance=between,between_within_ratio=ratio,fisher_ratio=fisher,knn_cross_mix=mix,
                linear_probe_acc=probe,nearest_centroid_acc=cent,stable_rank=stable,effective_rank=eff,pc1_mode_alignment=pc_align,
                pair_delta_alignment=delta_align,pair_delta_sign_consistency=sign,pair_delta_norm=delta_norm),spec

# Raw tokencode geometry (byte unigram + exact byte bigram counts, L2 norm)
def byte_features(items):
    rows=[]; cols=[]; vals=[]
    D=256+65536
    for i,(_,_,s) in enumerate(items):
        b=list(s.encode('utf-8'))[:MAXLEN-1]
        cnt={}
        for x in b: cnt[x]=cnt.get(x,0)+1
        for a,b2 in zip(b,b[1:]):
            j=256+a*256+b2; cnt[j]=cnt.get(j,0)+1
        norm=math.sqrt(sum(v*v for v in cnt.values())) or 1
        for j,v in cnt.items(): rows.append(i); cols.append(j); vals.append(v/norm)
    return sparse.csr_matrix((vals,(rows,cols)),shape=(len(items),D),dtype=np.float32)

Btr=byte_features(train_items); Bte=byte_features(test_items)
# dense projection for geometry using all held-out features occurring in train/test; exact, no hash
cols=np.unique(np.concatenate([Btr.indices,Bte.indices])); btr=Btr[:,cols].toarray(); bte=Bte[:,cols].toarray()
raw_geo,raw_spec=geo(bte,Yte.numpy(),btr,Ytr.numpy(),[x[0] for x in test_items])

# Extract trained and untrained activations
trained=copy.deepcopy(model)
untrained=TinyCausal(); untrained.load_state_dict(init_state)
logT,lastT,meanT,cloudT=extract(trained,Xte,Lte)
_,lastTr,meanTr,_=extract(trained,Xtr,Ltr)
logU,lastU,meanU,cloudU=extract(untrained,Xte,Lte)
_,lastUtr,meanUtr,_=extract(untrained,Xtr,Ltr)

rows=[]; spectra=[]
rawrow={'stage':'tokencode_0','layer':0,'representation':'byte_uni_bigram','trained':False,**raw_geo}
rows.append(rawrow)
for j,v in enumerate(raw_spec): spectra.append({'stage':'tokencode_0','layer':0,'trained':False,'component':j+1,'energy_fraction':float(v)})

pairids=[x[0] for x in test_items]
for trainedflag, lasts,means,clouds,tr_lasts,tr_means in [
    (False,lastU,meanU,cloudU,lastUtr,meanUtr),(True,lastT,meanT,cloudT,lastTr,meanTr)]:
    for li in range(len(lasts)):
        for rep,Z,Ztr in [('decision_last_token',lasts[li],tr_lasts[li]),('sequence_mean',means[li],tr_means[li])]:
            g,spec=geo(Z,Yte.numpy(),Ztr,Ytr.numpy(),pairids)
            cstable,ceff,cspec=eranks(clouds[li])
            g['token_cloud_stable_rank']=cstable; g['token_cloud_effective_rank']=ceff
            rows.append({'stage':'model','layer':li,'representation':rep,'trained':trainedflag,**g})
            for j,v in enumerate(spec): spectra.append({'stage':'model','layer':li,'representation':rep,'trained':trainedflag,'component':j+1,'energy_fraction':float(v)})

pd.DataFrame(rows).to_csv('MODE_COLLISION_001_layerwise_geometry.csv',index=False)
pd.DataFrame(spectra).to_csv('MODE_COLLISION_001_layerwise_spectra.csv',index=False)
pd.DataFrame(hist,columns=['epoch','loss','train_acc','heldout_acc']).to_csv('MODE_COLLISION_001_training_curve.csv',index=False)

summary={
 'pairs_total':len(PAIRS),'train_pairs':len(train_pairs),'heldout_pairs':len(test_pairs),
 'model':{'layers':8,'d_model':24,'heads':4,'ff':64,'tokenization':'UTF-8 byte tokencode, BOS + byte codes, max 128 (prefix+suffix preservation)'},
 'final_train_acc':hist[-1][2],'final_heldout_acc':hist[-1][3],
 'tokencode_geometry':raw_geo,
}
# key trained decision curve
rdf=pd.DataFrame(rows); q=rdf[(rdf.stage=='model')&(rdf.trained==True)&(rdf.representation=='decision_last_token')].sort_values('layer')
summary['decision_curve']=q[['layer','knn_cross_mix','fisher_ratio','linear_probe_acc','nearest_centroid_acc','between_within_ratio','stable_rank','effective_rank','pair_delta_alignment','pair_delta_sign_consistency','pc1_mode_alignment']].to_dict('records')
summary['max_fisher_layer']=int(q.loc[q.fisher_ratio.idxmax(),'layer'])
summary['min_mix_layer']=int(q.loc[q.knn_cross_mix.idxmin(),'layer'])
summary['max_probe_layer']=int(q.loc[q.linear_probe_acc.idxmax(),'layer'])
json.dump(summary,open('MODE_COLLISION_001_summary.json','w'),ensure_ascii=False,indent=2)
# save weights for reproducibility
# torch.save(trained.state_dict(),'MODE_COLLISION_001_tiny_transformer.pt')
print(json.dumps(summary,ensure_ascii=False)[:12000])
