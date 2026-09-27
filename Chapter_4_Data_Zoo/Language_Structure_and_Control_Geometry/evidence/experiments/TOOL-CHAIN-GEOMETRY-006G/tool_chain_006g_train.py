import os,json,random,hashlib,time,shutil,importlib.util
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader,TensorDataset

OUT='/mnt/data/tool_chain_006g_evidence';os.makedirs(OUT,exist_ok=True)
SEED=26093041
random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED);torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))
# import only world/task primitives from final 006D source
spec=importlib.util.spec_from_file_location('d6','/mnt/data/006d_unpack/tool_chain_006d_final_evidence/tool_chain_006d_final_eval.py')
d6=importlib.util.module_from_spec(spec)
# avoid executing bottom experiment block
src=open(spec.origin).read();prefix=src.split("OUT='/mnt/data/tool_chain_006d_final_evidence'")[0];ns={};exec(prefix,ns)
Action=ns['Action'];Task=ns['Task'];Cell=ns['Cell'];KEYS=ns['KEYS'];VALS=ns['VALS'];NONE=ns['NONE'];TOOLS=ns['TOOLS'];KINDS=ns['KINDS'];ROLE_FIELDS=ns['ROLE_FIELDS'];make_task=ns['make_task'];emit_json=ns['emit_json'];ok_write=ns['ok_write'];ok_clear=ns['ok_clear']
CELLS=[Cell('P1_N1',1,1),Cell('P1_N0',1,0),Cell('P0_N1',0,1),Cell('P0_N0',0,0)]
SEEN_STYLES=(0,1,2);UNSEEN_STYLES=(3,4,5)

def raw_obj(cid,v,style,provenance=True):
    if style==0:
        o={'data':{'value':f'{v:02d}'}}
        if provenance:o['id']=cid
    elif style==1:
        o={'result':{'number':v,'unit':'register_value'}}
        if provenance:o['request']=cid
    elif style==2:
        o={'payload':[v]}
        if provenance:o['call']=cid
    elif style==3:
        o={'observation':{'reading':f'{v} units'}}
        if provenance:o['trace']=cid
    elif style==4:
        o={'reply':[{'scalar':v}]}
        if provenance:o['request_ref']=cid
    elif style==5:
        o={'measurement':{'digit':str(v)}}
        if provenance:o['origin']=cid
    else: raise ValueError(style)
    return o

def result_line(cid,v,cell,style):
    if cell.normalization:
        o={'value':v}
        if cell.provenance:o['call_id']=cid
    else:
        o=raw_obj(cid,v,style,bool(cell.provenance))
    return 'RESULT '+json.dumps(o,separators=(',',':'),sort_keys=True)

def parse_result_event(o,call_key):
    # canonical codes 0..9; raw style codes 10..69; 70 = empty slot
    if not isinstance(o,dict): return None,None,None
    if 'value' in o and isinstance(o.get('value'),int):
        return o['value'], call_key.get(o.get('call_id')) if 'call_id' in o else None,'canonical'
    style=None;v=None;cid=None
    try:
        if isinstance(o.get('data'),dict) and 'value' in o['data']:
            style=0;v=int(o['data']['value']);cid=o.get('id')
        elif isinstance(o.get('result'),dict) and isinstance(o['result'].get('number'),int):
            style=1;v=o['result']['number'];cid=o.get('request')
        elif isinstance(o.get('payload'),list) and o['payload'] and isinstance(o['payload'][0],int):
            style=2;v=o['payload'][0];cid=o.get('call')
        elif isinstance(o.get('observation'),dict) and isinstance(o['observation'].get('reading'),str):
            style=3;v=int(o['observation']['reading'].split()[0]);cid=o.get('trace')
        elif isinstance(o.get('reply'),list) and o['reply'] and isinstance(o['reply'][0],dict):
            style=4;v=int(o['reply'][0]['scalar']);cid=o.get('request_ref')
        elif isinstance(o.get('measurement'),dict) and 'digit' in o['measurement']:
            style=5;v=int(o['measurement']['digit']);cid=o.get('origin')
    except Exception:
        return None,None,None
    if style is None or not (0<=v<=9): return None,None,None
    return 10+10*style+v, call_key.get(cid) if cid is not None else None,f'raw{style}'

# symmetric event slots with reserve for unseen raw codes
KIND_OFF=0;ROLE_OFF=KIND_OFF+len(KINDS);ROLE_W=len(ROLE_FIELDS)*len(KEYS)
RES_OFF=ROLE_OFF+ROLE_W;RES_SLOTS=4;VALCODE_W=71;PROV_W=9;MATCH_W=len(ROLE_FIELDS);RES_SLOT_W=VALCODE_W+PROV_W+MATCH_W;RES_W=RES_SLOTS*RES_SLOT_W
LASTACT_OFF=RES_OFF+RES_W;LASTACT_W=3*(len(TOOLS)+len(KEYS)+len(KEYS)+11)
COUNT_OFF=LASTACT_OFF+LASTACT_W;COUNT_W=len(TOOLS)+1
VERIFY_OFF=COUNT_OFF+COUNT_W;VERIFY_W=len(KEYS)*11+2
D=VERIFY_OFF+VERIFY_W

def features(lines):
    f=np.zeros(D,dtype=np.float32);request=None;call_key={};events=[];acts=[];counts={t:0 for t in TOOLS};schema=0;verify=None;vf=0
    for line in lines:
        if line.startswith('REQUEST '):
            try:request=json.loads(line[8:])
            except:pass
        elif line.startswith('CALL '):
            try:o=json.loads(line[5:]);call_key[o.get('id')]=o.get('key')
            except:pass
        elif line.startswith('RESULT '):
            try:o=json.loads(line[7:])
            except:continue
            code,key,style=parse_result_event(o,call_key)
            if code is not None:events.append((code,key,style))
        elif line.startswith('ACTION '):
            try:
                o=json.loads(line[7:]);tool=o.get('tool',NONE);k1=o.get('key',o.get('key1',NONE));k2=o.get('key2',NONE);val=o.get('value',-1);acts.append((tool,k1,k2,val));counts[tool]=counts.get(tool,0)+1
            except:pass
        elif line.startswith('SCHEMA_ERROR'):schema=1
        elif line.startswith('VERIFY_FAIL '):
            vf=1
            try:verify=json.loads(line[12:])
            except:pass
    if request:
        k=request.get('task','').upper()
        if k in KINDS:f[KIND_OFF+KINDS.index(k)]=1
        for ri,r in enumerate(ROLE_FIELDS):
            v=request.get(r)
            if v in KEYS:f[ROLE_OFF+ri*len(KEYS)+KEYS.index(v)]=1
    ev=events[-RES_SLOTS:][::-1]
    for j in range(RES_SLOTS):
        base=RES_OFF+j*RES_SLOT_W
        if j<len(ev):
            code,key,_=ev[j];f[base+code]=1
            pk=0 if key not in KEYS else KEYS.index(key)+1;f[base+VALCODE_W+pk]=1
            if request and key in KEYS:
                for ri,r in enumerate(ROLE_FIELDS):
                    if request.get(r)==key:f[base+VALCODE_W+PROV_W+ri]=1
        else:
            f[base+70]=1;f[base+VALCODE_W]=1
    for j,a in enumerate(acts[-3:][::-1]):
        tool,k1,k2,val=a;base=LASTACT_OFF+j*(len(TOOLS)+len(KEYS)+len(KEYS)+11)
        if tool in TOOLS:f[base+TOOLS.index(tool)]=1
        if k1 in KEYS:f[base+len(TOOLS)+KEYS.index(k1)]=1
        if k2 in KEYS:f[base+len(TOOLS)+len(KEYS)+KEYS.index(k2)]=1
        ix=0 if not(isinstance(val,int) and 0<=val<=9) else val+1;f[base+len(TOOLS)+2*len(KEYS)+ix]=1
    for ti,t in enumerate(TOOLS):f[COUNT_OFF+ti]=min(counts.get(t,0),6)/6
    f[COUNT_OFF+len(TOOLS)]=schema
    if verify:
        for ki,k in enumerate(KEYS):
            exp=verify[k].get('expected') if k in verify and isinstance(verify[k],dict) else None;ix=0 if not isinstance(exp,int) else exp+1;f[VERIFY_OFF+ki*11+ix]=1
    f[VERIFY_OFF+len(KEYS)*11]=vf;f[VERIFY_OFF+len(KEYS)*11+1]=1 if vf and verify else 0
    return f

def style_for(seed,ci,styles):
    return styles[random.Random(seed*1000003+ci*9176+12345).randrange(len(styles))]

def append_exec(lines,world,a,ctr,rng,cell,seed,styles=SEEN_STYLES):
    lines.append('ACTION '+emit_json(a))
    if a.tool=='READ':
        ctr+=1;cid=f'c{ctr}';lines.append('CALL '+json.dumps({'id':cid,'tool':'READ','key':a.k1},separators=(',',':'),sort_keys=True));v=world[a.k1];lines.append(result_line(cid,v,cell,style_for(seed,ctr,styles)))
    elif a.tool=='READPAIR':
        calls=[]
        for k in (a.k1,a.k2):
            ctr+=1;cid=f'c{ctr}';lines.append('CALL '+json.dumps({'id':cid,'tool':'READ','key':k},separators=(',',':'),sort_keys=True));calls.append((cid,k,world[k],ctr))
        rng.shuffle(calls)
        for cid,k,v,ci in calls:lines.append(result_line(cid,v,cell,style_for(seed,ci,styles)))
    elif a.tool=='WRITE':world[a.k1]=a.value;lines.append(ok_write(a.k1,a.value))
    elif a.tool=='CLEAR':world[a.k1]=0;lines.append(ok_clear(a.k1))
    return ctr

SPECIAL=['<PAD>','<BOS>','<EOS>'];TOOL_T=[f'TOOL_{x}' for x in TOOLS];K1_T=[f'K1_{x}' for x in [NONE]+KEYS];K2_T=[f'K2_{x}' for x in [NONE]+KEYS];V_T=[f'V_{x}' for x in [-1]+VALS];VOCAB=SPECIAL+TOOL_T+K1_T+K2_T+V_T;stoi={t:i for i,t in enumerate(VOCAB)}
def action_seq(a):return [stoi['<BOS>'],stoi[f'TOOL_{a.tool}'],stoi[f'K1_{a.k1}'],stoi[f'K2_{a.k2}'],stoi[f'V_{a.value}'],stoi['<EOS>']]
def seq_action(ids):
    if len(ids)!=4:return None,'length'
    ts=[VOCAB[i] if 0<=i<len(VOCAB) else '' for i in ids]
    if not(ts[0].startswith('TOOL_') and ts[1].startswith('K1_') and ts[2].startswith('K2_') and ts[3].startswith('V_')):return None,'slot'
    try:a=Action(ts[0][5:],ts[1][3:],ts[2][3:],int(ts[3][2:]))
    except:return None,'value'
    if a.tool=='READ':ok=a.k1 in KEYS and a.k2==NONE and a.value==-1
    elif a.tool=='READPAIR':ok=a.k1 in KEYS and a.k2 in KEYS and a.k1!=a.k2 and a.value==-1
    elif a.tool=='WRITE':ok=a.k1 in KEYS and a.k2==NONE and a.value in VALS
    elif a.tool=='CLEAR':ok=a.k1 in KEYS and a.k2==NONE and a.value==-1
    elif a.tool=='DONE':ok=a.k1==NONE and a.k2==NONE and a.value==-1
    else:ok=False
    return (a,None) if ok else (a,'schema')
class GenPlanner(nn.Module):
    def __init__(self,d,v,emb=48,ctx=160,hid=192):
        super().__init__();self.emb=nn.Embedding(v,emb,padding_idx=0);self.ctx=nn.Sequential(nn.Linear(d,256),nn.ReLU(),nn.Linear(256,ctx),nn.ReLU());self.h0=nn.Linear(ctx,hid);self.gru=nn.GRU(emb+ctx,hid,batch_first=True);self.out=nn.Linear(hid,v)
    def forward(self,x,tok):
        c=self.ctx(x);h=torch.tanh(self.h0(c)).unsqueeze(0);e=self.emb(tok);cc=c[:,None,:].expand(-1,e.size(1),-1);z,_=self.gru(torch.cat([e,cc],-1),h);return self.out(z)
    def start(self,x):c=self.ctx(x);return c,torch.tanh(self.h0(c)).unsqueeze(0)
    def step(self,t,c,h):e=self.emb(t);z,h=self.gru(torch.cat([e,c[:,None,:]],-1),h);return self.out(z[:,-1]),h
@torch.no_grad()
def generate(m,x):
    xt=torch.tensor(x[None,:],dtype=torch.float32);c,h=m.start(xt);cur=torch.tensor([[stoi['<BOS>']]],dtype=torch.long);outs=[]
    for _ in range(4):log,h=m.step(cur,c,h);i=int(log.argmax(-1));outs.append(i);cur=torch.tensor([[i]])
    log,h=m.step(cur,c,h);eos=int(log.argmax(-1))==stoi['<EOS>'];a,err=seq_action(outs);return a,err,eos,outs

def build_data(n_tasks=6000):
    rr=random.Random(SEED+1);X=[];Y=[]
    for ti in range(n_tasks):
        t=make_task(rr)
        for ci,cell in enumerate(CELLS):
            rng=random.Random(SEED+100000+ti*17+ci);lines=[t.request];w=t.init.copy();ctr=0
            for a in t.oracle:
                X.append(features(lines));Y.append(action_seq(a))
                if a.tool=='DONE':break
                ctr=append_exec(lines,w,a,ctr,rng,cell,SEED+ti*31+ci,SEEN_STYLES)
        if (ti+1)%1000==0:print('BUILD',ti+1,flush=True)
    return np.stack(X).astype('float32'),np.asarray(Y,dtype=np.int64)

def prefix_pilot(m,n_tasks=300,styles=SEEN_STYLES):
    rr=random.Random(SEED+51000);n=exact=valid=0;by={c.name:[0,0] for c in CELLS}
    for ti in range(n_tasks):
        t=make_task(rr)
        for ci,cell in enumerate(CELLS):
            rng=random.Random(SEED+200000+ti*13+ci);lines=[t.request];w=t.init.copy();ctr=0
            for oracle in t.oracle:
                a,err,_,_=generate(m,features(lines));n+=1;valid+=err is None;exact+=int(err is None and a.tup()==oracle.tup());by[cell.name][1]+=1;by[cell.name][0]+=int(err is None and a.tup()==oracle.tup())
                if oracle.tool=='DONE':break
                ctr=append_exec(lines,w,oracle,ctr,rng,cell,SEED+ti*29+ci,styles)
    return {'n':n,'exact':exact/n,'valid':valid/n,'by_cell':{k:v[0]/v[1] for k,v in by.items()}}

def run_episode(m,t,cell,seed,styles=SEEN_STYLES,max_steps=14):
    rng=random.Random(seed);w=t.init.copy();lines=[t.request];ctr=0;oi=0;fd=0;perr=sch=vf=0
    for step in range(max_steps):
        a,err,_,ids=generate(m,features(lines))
        if err:
            perr+=1;sch+=int(err=='schema');lines.append('PLANNER_GENERATION_ERROR '+json.dumps({'error':err,'tokens':[VOCAB[i] for i in ids]},separators=(',',':')))
            if perr>=3:break
            continue
        if not fd and a.tup()!=t.oracle[min(oi,len(t.oracle)-1)].tup():fd=step+1
        oi+=1
        if a.tool in ('READ','READPAIR','WRITE','CLEAR'):ctr=append_exec(lines,w,a,ctr,rng,cell,seed+step,styles)
        else:
            lines.append('ACTION '+emit_json(a))
            if w==t.target:lines.append('VERIFY_OK');return {'ok':1,'first_div':fd,'planner_errors':perr,'schema_errors':sch,'steps':step+1}
            vf+=1;diff={k:{'expected':t.target[k],'observed':w[k]} for k in KEYS if w[k]!=t.target[k]};lines+=['STATE '+json.dumps(w,separators=(',',':'),sort_keys=True),'VERIFY_FAIL '+json.dumps(diff,separators=(',',':'),sort_keys=True)]
            if vf>=2:break
    return {'ok':int(w==t.target),'first_div':fd,'planner_errors':perr,'schema_errors':sch,'steps':max_steps}

def baseline_pilot(m,n_tasks=240):
    rr=random.Random(SEED+52000);tasks=[make_task(rr) for _ in range(n_tasks)];out={}
    for cell in CELLS[:2]:
        rs=[run_episode(m,t,cell,SEED+700000+i,SEEN_STYLES) for i,t in enumerate(tasks)]
        out[cell.name]=sum(r['ok'] for r in rs)/len(rs)
    return out

def main():
    X,Y=build_data(6000);print('DATA',X.shape,Y.shape,'D',D,'V',len(VOCAB),flush=True)
    xt=torch.tensor(X,dtype=torch.float32);inp=torch.tensor(Y[:,:-1],dtype=torch.long);tgt=torch.tensor(Y[:,1:],dtype=torch.long);dl=DataLoader(TensorDataset(xt,inp,tgt),batch_size=1536,shuffle=True,num_workers=0)
    m=GenPlanner(D,len(VOCAB));opt=torch.optim.AdamW(m.parameters(),lr=2.5e-3,weight_decay=1e-5);hist=[]
    for ep in range(3):
        m.train();num=den=0.0
        for xb,ib,tb in dl:
            opt.zero_grad(set_to_none=True);log=m(xb,ib);loss=nn.functional.cross_entropy(log.reshape(-1,len(VOCAB)),tb.reshape(-1));loss.backward();nn.utils.clip_grad_norm_(m.parameters(),1.0);opt.step();num+=float(loss.detach())*len(xb);den+=len(xb)
        hist.append(num/den);pil=prefix_pilot(m,120,SEEN_STYLES);print('EPOCH',ep+1,'NLL',hist[-1],'PFX',pil['exact'],'BY',pil['by_cell'],flush=True)
        torch.save({'state':m.state_dict(),'vocab':VOCAB,'D':D,'emb':48,'ctx':160,'hid':192,'seed':SEED,'history':hist,'seen_styles':SEEN_STYLES,'unseen_styles':UNSEEN_STYLES},OUT+'/planner.pt')
    m.eval();pp=prefix_pilot(m,350,SEEN_STYLES);bp=baseline_pilot(m,240)
    gate={'prefix_exact_threshold':0.85,'canonical_final_threshold':0.65,'seen_raw_final_threshold':0.65,'passed':bool(pp['exact']>=0.85 and bp['P1_N1']>=0.65 and bp['P1_N0']>=0.65)}
    res={'experiment':'TOOL-CHAIN-GEOMETRY-006G pilot gate','seed':SEED,'train_tasks':6000,'train_actions':len(Y),'feature_dim':D,'training_nll':hist,'seen_styles':SEEN_STYLES,'heldout_styles':UNSEEN_STYLES,'prefix_pilot_seen':pp,'baseline_seen':bp,'prospective_gate':gate}
    json.dump(res,open(OUT+'/pilot_gate.json','w'),indent=2);shutil.copy2(__file__,OUT+'/train.py');print('GATE',json.dumps(res),flush=True)
if __name__=='__main__':main()
