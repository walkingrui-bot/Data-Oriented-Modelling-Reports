import os,json,random,re,hashlib,csv,shutil
from collections import Counter,defaultdict
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader,Dataset

OUT='/mnt/data/tool_chain_006e_ar_evidence';os.makedirs(OUT,exist_ok=True)
SEED_E=26092771
random.seed(SEED_E);np.random.seed(SEED_E);torch.manual_seed(SEED_E);torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))

# Reuse the exact 006D world, symmetric event reader, raw-style generator and executor.
SRC='/mnt/data/tool_chain_006d_final_evidence/tool_chain_006d_final_eval.py'
source=open(SRC).read();prefix=source.split("OUT='/mnt/data/tool_chain_006d_final_evidence'")[0]
ns={};exec(prefix,ns)
Action=ns['Action'];Task=ns['Task'];Cell=ns['Cell'];CELLS=ns['CELLS'];KEYS=ns['KEYS'];VALS=ns['VALS'];TOOLS=ns['TOOLS'];NONE=ns['NONE'];KINDS=ns['KINDS'];D=ns['D']
make_task=ns['make_task'];features=ns['features'];append_exec=ns['append_exec'];emit_json=ns['emit_json'];ok_write=ns['ok_write'];emit_obj=ns['emit_obj']

PAT=re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|-?\d+|[A-Za-z_<>]+|[{}\[\]:,]|[^\s]')
def atoks(a):return PAT.findall(emit_json(a))
SPECIAL=['<PAD>','<BOS>','<EOS>','<UNK>']

def valid_obj(o):
    if not isinstance(o,dict) or o.get('tool') not in TOOLS:return False
    t=o['tool']
    if t=='READ':return set(o)=={'tool','key'} and o.get('key') in KEYS
    if t=='READPAIR':return set(o)=={'tool','key1','key2'} and o.get('key1') in KEYS and o.get('key2') in KEYS and o['key1']!=o['key2']
    if t=='WRITE':return set(o)=={'tool','key','value'} and o.get('key') in KEYS and isinstance(o.get('value'),int) and o['value'] in VALS
    if t=='CLEAR':return set(o)=={'tool','key'} and o.get('key') in KEYS
    return set(o)=={'tool'}
def obj_action(o):
    t=o['tool']
    if t=='READPAIR':return Action(t,o['key1'],o['key2'])
    if t=='WRITE':return Action(t,o['key'],value=o['value'])
    if t in ('READ','CLEAR'):return Action(t,o['key'])
    return Action('DONE')

def build_data(n_tasks=2000):
    rr=random.Random(SEED_E+1); xs=[]; seqs=[]; vocab=Counter()
    for ti in range(n_tasks):
        t=make_task(rr)
        for ci,cell in enumerate(CELLS):
            rng=random.Random(SEED_E+100000+ti*31+ci);lines=[t.request];world=t.init.copy();ctr=0
            for a in t.oracle:
                xs.append(features(lines));q=atoks(a);seqs.append(q);vocab.update(q)
                if a.tool=='DONE':break
                ctr=append_exec(lines,world,a,ctr,rng,cell,ti*13+ci)
        if ti%3==0:
            bad=t.target.copy();r2=random.Random(SEED_E+ti);k=r2.choice(KEYS);bad[k]=(bad[k]+r2.randrange(1,10))%10
            diff={kk:{'expected':t.target[kk],'observed':bad[kk]} for kk in KEYS if bad[kk]!=t.target[kk]}
            l2=[t.request,'STATE '+json.dumps(bad,separators=(',',':'),sort_keys=True),'VERIFY_FAIL '+json.dumps(diff,separators=(',',':'),sort_keys=True)]
            fix=Action('WRITE',k,value=t.target[k])
            for lines,a in [(l2,fix),(l2+['ACTION '+emit_json(fix),ok_write(k,t.target[k]),'VERIFY_OK'],Action('DONE'))]:
                xs.append(features(lines));q=atoks(a);seqs.append(q);vocab.update(q)
    vocab=SPECIAL+sorted(vocab.keys());stoi={t:i for i,t in enumerate(vocab)}
    ys=[]
    for q in seqs:ys.append([stoi['<BOS>']]+[stoi.get(x,stoi['<UNK>']) for x in q]+[stoi['<EOS>']])
    return np.stack(xs).astype('float32'),ys,vocab,stoi

class DS(Dataset):
    def __init__(self,X,Y):self.X=X;self.Y=Y
    def __len__(self):return len(self.Y)
    def __getitem__(self,i):return self.X[i],self.Y[i]
def collate(b):
    X=torch.tensor(np.stack([x for x,_ in b]),dtype=torch.float32);L=max(len(y) for _,y in b);inp=torch.zeros((len(b),L-1),dtype=torch.long);tgt=torch.zeros((len(b),L-1),dtype=torch.long);mask=torch.zeros((len(b),L-1),dtype=torch.float32)
    for i,(_,y) in enumerate(b):
        n=len(y)-1;inp[i,:n]=torch.tensor(y[:-1]);tgt[i,:n]=torch.tensor(y[1:]);mask[i,:n]=1
    return X,inp,tgt,mask

class ARPolicy(nn.Module):
    def __init__(self,d,v,emb=32,hid=96):
        super().__init__();self.emb=nn.Embedding(v,emb,padding_idx=0);self.init=nn.Sequential(nn.Linear(d,128),nn.ReLU(),nn.Linear(128,hid),nn.Tanh());self.gru=nn.GRU(emb,hid,batch_first=True);self.out=nn.Linear(hid,v)
    def forward(self,x,tok):
        h=self.init(x).unsqueeze(0);z,_=self.gru(self.emb(tok),h);return self.out(z)
    def start(self,x):return self.init(x).unsqueeze(0)
    def step(self,t,h):
        z,h=self.gru(self.emb(t),h);return self.out(z[:,-1]),h

def train():
    X,Y,vocab,stoi=build_data();ds=DS(X,Y);dl=DataLoader(ds,batch_size=1024,shuffle=True,collate_fn=collate,num_workers=0)
    m=ARPolicy(D,len(vocab));opt=torch.optim.AdamW(m.parameters(),lr=3e-3,weight_decay=1e-5);hist=[]
    for ep in range(3):
        m.train();num=den=0.0
        for x,inp,tgt,mask in dl:
            opt.zero_grad(set_to_none=True);log=m(x,inp);ls=nn.functional.cross_entropy(log.reshape(-1,len(vocab)),tgt.reshape(-1),reduction='none').reshape_as(tgt);loss=(ls*mask).sum()/mask.sum();loss.backward();nn.utils.clip_grad_norm_(m.parameters(),1.0);opt.step();num+=float((ls*mask).sum().detach());den+=float(mask.sum())
        hist.append(num/den);print('EPOCH',ep+1,'NLL',hist[-1],flush=True)
    torch.save({'state':m.state_dict(),'vocab':vocab,'hist':hist,'D':D,'emb':32,'hid':96,'seed':SEED_E,'train_actions':len(Y)},OUT+'/ar_policy.pt')
    json.dump({'nll':hist,'train_actions':len(Y),'feature_dim':D,'vocab_size':len(vocab)},open(OUT+'/training_history.json','w'),indent=2)
    return m,vocab,stoi,hist,len(Y)
def load():
    z=torch.load(OUT+'/ar_policy.pt',map_location='cpu');m=ARPolicy(z['D'],len(z['vocab']),z['emb'],z['hid']);m.load_state_dict(z['state']);m.eval();return m,z['vocab'],{t:i for i,t in enumerate(z['vocab'])},z['hist'],z['train_actions']

@torch.no_grad()
def gen(m,vocab,stoi,lines,max_new=24):
    x=torch.tensor(features(lines)[None,:],dtype=torch.float32);h=m.start(x);cur=torch.tensor([[stoi['<BOS>']]],dtype=torch.long);out=[]
    for _ in range(max_new):
        log,h=m.step(cur,h);i=int(log.argmax(-1));tok=vocab[i]
        if tok=='<EOS>':break
        if tok in ('<PAD>','<BOS>'):break
        out.append(tok);cur=torch.tensor([[i]],dtype=torch.long)
    return ''.join(out)

def run_ep(m,vocab,stoi,t,cell,seed,max_steps=14):
    rng=random.Random(seed);w=t.init.copy();lines=[t.request];ctr=0;oi=0;fd=0;syn=0;sch=0;vf=0;rec=0;had=False;generated=[]
    for step in range(max_steps):
        txt=gen(m,vocab,stoi,lines);generated.append(txt)
        try:o=json.loads(txt)
        except:
            syn+=1;lines+=['ACTION_TEXT '+txt,'SYNTAX_ERROR'];
            if syn>=3:break
            continue
        if not valid_obj(o):
            sch+=1;lines+=['ACTION_TEXT '+txt,'SCHEMA_ERROR '+json.dumps({'error':'invalid_tool_arguments'},separators=(',',':'))]
            if sch>=3:break
            continue
        a=obj_action(o)
        if not fd and a.tup()!=t.oracle[min(oi,len(t.oracle)-1)].tup():fd=step+1
        oi+=1
        if a.tool in ('READ','READPAIR','WRITE','CLEAR'):
            ctr=append_exec(lines,w,a,ctr,rng,cell,seed+step)
        else:
            lines.append('ACTION '+emit_json(a))
            if w==t.target:
                if had:rec=1
                lines.append('VERIFY_OK');return {'ok':1,'steps':step+1,'first_div':fd,'syntax_errors':syn,'schema_errors':sch,'verify_failures':vf,'recovered':rec,'trace':lines,'generated':generated,'world':w}
            vf+=1;had=True;diff={k:{'expected':t.target[k],'observed':w[k]} for k in KEYS if w[k]!=t.target[k]};lines+=['STATE '+json.dumps(w,separators=(',',':'),sort_keys=True),'VERIFY_FAIL '+json.dumps(diff,separators=(',',':'),sort_keys=True)]
            if vf>=2:break
    return {'ok':0,'steps':max_steps,'first_div':fd or max_steps+1,'syntax_errors':syn,'schema_errors':sch,'verify_failures':vf,'recovered':rec,'trace':lines,'generated':generated,'world':w}

def pilot(m,vocab,stoi):
    rr=random.Random(SEED_E+51);n=ex=jp=sv=0
    for ti in range(180):
        t=make_task(rr);cell=CELLS[ti%4];rng=random.Random(SEED_E+1000+ti);lines=[t.request];w=t.init.copy();ctr=0
        for a in t.oracle:
            txt=gen(m,vocab,stoi,lines);n+=1;ex+=int(txt==emit_json(a))
            try:o=json.loads(txt);jp+=1;sv+=int(valid_obj(o))
            except:pass
            if a.tool=='DONE':break
            ctr=append_exec(lines,w,a,ctr,rng,cell,ti)
    return {'n':n,'oracle_exact':ex/n,'json_parse':jp/n,'schema_valid':sv/n}

def evaluate(m,vocab,stoi,n_panel=200):
    rows=[];tr=[]
    for pi,ps in enumerate([SEED_E+101,SEED_E+202,SEED_E+303]):
        rr=random.Random(ps);tasks=[make_task(rr) for _ in range(n_panel)]
        for ti,t in enumerate(tasks):
            reads=sum(1 if a.tool=='READ' else 2 if a.tool=='READPAIR' else 0 for a in t.oracle)
            for ci,c in enumerate(CELLS):
                z=run_ep(m,vocab,stoi,t,c,ps*10000+ti*19+ci)
                rows.append({'panel':pi+1,'task_i':ti,'kind':t.kind,'read_count':reads,'cell':c.name,'provenance':int(c.provenance),'normalization':int(c.normalization),'ok':z['ok'],'steps':z['steps'],'first_div':z['first_div'],'syntax_errors':z['syntax_errors'],'schema_errors':z['schema_errors'],'verify_failures':z['verify_failures'],'recovered':z['recovered']})
                if len(tr)<30 and ((not z['ok'] and ci==0) or z['syntax_errors'] or z['schema_errors'] or (ti<2 and ci==0)):
                    tr.append({'panel':pi+1,'task_i':ti,'kind':t.kind,'cell':c.name,'request':t.request,'init':t.init,'target':t.target,'result':{k:z[k] for k in ['ok','steps','first_div','syntax_errors','schema_errors','verify_failures','recovered']},'generated':z['generated'],'trace':z['trace']})
        print('PANEL',pi+1,'done',flush=True)
    return rows,tr

def summary(rows):
    mean=lambda a:sum(a)/len(a) if a else float('nan')
    cs={}
    for c in [x.name for x in CELLS]:
        q=[r for r in rows if r['cell']==c];cs[c]={'n':len(q),'acc':mean([r['ok'] for r in q]),'syntax_any':mean([r['syntax_errors']>0 for r in q]),'schema_any':mean([r['schema_errors']>0 for r in q]),'recovery_rate':mean([r['recovered'] for r in q]),'first_div_mean':mean([r['first_div'] for r in q])}
    by=defaultdict(dict)
    for r in rows:by[(r['panel'],r['task_i'])][r['cell']]=r['ok']
    vals=[]
    for d in by.values():
        if len(d)==4:vals.append(((d['P1_N1']+d['P1_N0']-d['P0_N1']-d['P0_N0'])/2,(d['P1_N1']+d['P0_N1']-d['P1_N0']-d['P0_N0'])/2,d['P1_N1']-d['P1_N0']-d['P0_N1']+d['P0_N0']))
    A=np.asarray(vals);eff={'provenance':float(A[:,0].mean()),'normalization':float(A[:,1].mean()),'interaction':float(A[:,2].mean())}
    br=random.Random(SEED_E+999);boots={k:[] for k in eff}
    for _ in range(1500):
        ix=[br.randrange(len(A)) for _ in range(len(A))];B=A[ix]
        for j,k in enumerate(['provenance','normalization','interaction']):boots[k].append(float(B[:,j].mean()))
    ci={k:[float(np.quantile(v,.025)),float(np.quantile(v,.975))] for k,v in boots.items()}
    strata={}
    for lab,pred in [('single_read',lambda r:r['read_count']==1),('multi_read',lambda r:r['read_count']>1)]:
        q=[r for r in rows if pred(r)];acc={c:mean([r['ok'] for r in q if r['cell']==c]) for c in [x.name for x in CELLS]};strata[lab]={'n_tasks':len(q)//4,'acc':acc,'interaction':acc['P1_N1']-acc['P1_N0']-acc['P0_N1']+acc['P0_N0']}
    panels={}
    for p in [1,2,3]:panels[str(p)]={c:mean([r['ok'] for r in rows if r['panel']==p and r['cell']==c]) for c in [x.name for x in CELLS]}
    return cs,eff,ci,strata,panels

def main():
    if os.path.exists(OUT+'/ar_policy.pt'):m,vocab,stoi,hist,nt=load()
    else:m,vocab,stoi,hist,nt=train()
    pil=pilot(m,vocab,stoi);print('PILOT',pil,flush=True)
    rows,tr=evaluate(m,vocab,stoi,200);cs,eff,ci,strata,panels=summary(rows)
    res={'experiment':'TOOL-CHAIN-GEOMETRY-006E','design':'same 006D event reader + unconstrained autoregressive JSON decoder','seed':SEED_E,'train_actions':nt,'training_nll':hist,'pilot':pil,'n_tasks':600,'n_trajectories':len(rows),'conditions':cs,'effects':eff,'effect_ci95':ci,'strata':strata,'panels':panels}
    json.dump(res,open(OUT+'/results.json','w'),indent=2);json.dump(tr,open(OUT+'/representative_traces.json','w'),indent=2)
    with open(OUT+'/episode_summary.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    shutil.copy2(SRC,OUT+'/006d_reader_reference.py');shutil.copy2(__file__,OUT+'/tool_chain_006e_autoregressive_json.py')
    man={'seed':SEED_E,'policy_sha256':hashlib.sha256(open(OUT+'/ar_policy.pt','rb').read()).hexdigest(),'script_sha256':hashlib.sha256(open(__file__,'rb').read()).hexdigest(),'reader_sha256':hashlib.sha256(open(SRC,'rb').read()).hexdigest(),'formal_rows':len(rows),'note':'Action JSON is generated token-by-token without grammar-constrained decoding. 006D event reader is held fixed to isolate output-generation modality.'};json.dump(man,open(OUT+'/source_manifest.json','w'),indent=2)
    print('RESULTS',json.dumps(res),flush=True)
if __name__=='__main__':main()
