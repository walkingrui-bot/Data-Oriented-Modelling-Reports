import os,json,random,hashlib,pickle
from dataclasses import dataclass
import numpy as np
from sklearn.tree import DecisionTreeClassifier

SEED=26092821
random.seed(SEED);np.random.seed(SEED)
KEYS=list('ABCDEFGH');VALS=list(range(10));NONE='<NONE>'
TOOLS=['READ','READPAIR','WRITE','CLEAR','DONE'];KINDS=['COPY','BACKUP_CLEAR','SWAP','DUAL_COPY','ROTATE3','DUPLICATE','MOVE2','FANOUT3','CHAIN_COPY']
ROLE_FIELDS=['src','dst','a','b','c','src1','dst1','src2','dst2','dst3','mid1','mid2']
@dataclass(frozen=True)
class Action:
    tool:str;k1:str=NONE;k2:str=NONE;value:int=-1
    def tup(self):return(self.tool,self.k1,self.k2,self.value)
@dataclass
class Task: kind:str;args:tuple;init:dict;payload:dict;request:str;target:dict;oracle:list
@dataclass(frozen=True)
class Cell: name:str;provenance:bool;normalization:bool
CELLS=[Cell('P1_N1',1,1),Cell('P1_N0',1,0),Cell('P0_N1',0,1),Cell('P0_N0',0,0)]

def make_task(rng,force_kind=None):
    init={k:rng.randrange(10) for k in KEYS};ks=rng.sample(KEYS,8);kind=force_kind or rng.choice(KINDS);target=init.copy();p={'task':kind.lower()}
    if kind=='COPY':s,d=ks[:2];p.update(src=s,dst=d);target[d]=init[s];oracle=[Action('READ',s),Action('WRITE',d,value=init[s]),Action('DONE')];args=(s,d)
    elif kind=='BACKUP_CLEAR':s,d=ks[:2];p.update(src=s,dst=d);target[d]=init[s];target[s]=0;oracle=[Action('READ',s),Action('WRITE',d,value=init[s]),Action('CLEAR',s),Action('DONE')];args=(s,d)
    elif kind=='SWAP':a,b=ks[:2];p.update(a=a,b=b);target[a],target[b]=init[b],init[a];oracle=[Action('READPAIR',a,b),Action('WRITE',a,value=init[b]),Action('WRITE',b,value=init[a]),Action('DONE')];args=(a,b)
    elif kind=='DUAL_COPY':a,b,c,d=ks[:4];p.update(src1=a,dst1=c,src2=b,dst2=d);target[c]=init[a];target[d]=init[b];oracle=[Action('READPAIR',a,b),Action('WRITE',c,value=init[a]),Action('WRITE',d,value=init[b]),Action('DONE')];args=(a,b,c,d)
    elif kind=='ROTATE3':a,b,c=ks[:3];p.update(a=a,b=b,c=c);target[b]=init[a];target[c]=init[b];target[a]=init[c];oracle=[Action('READPAIR',a,b),Action('READ',c),Action('WRITE',b,value=init[a]),Action('WRITE',c,value=init[b]),Action('WRITE',a,value=init[c]),Action('DONE')];args=(a,b,c)
    elif kind=='DUPLICATE':a,b,c=ks[:3];p.update(src=a,dst1=b,dst2=c);target[b]=target[c]=init[a];oracle=[Action('READ',a),Action('WRITE',b,value=init[a]),Action('WRITE',c,value=init[a]),Action('DONE')];args=(a,b,c)
    elif kind=='MOVE2':a,b,c,d=ks[:4];p.update(src1=a,dst1=c,src2=b,dst2=d);target[c]=init[a];target[d]=init[b];target[a]=0;target[b]=0;oracle=[Action('READPAIR',a,b),Action('WRITE',c,value=init[a]),Action('WRITE',d,value=init[b]),Action('CLEAR',a),Action('CLEAR',b),Action('DONE')];args=(a,b,c,d)
    elif kind=='FANOUT3':a,b,c,d=ks[:4];p.update(src=a,dst1=b,dst2=c,dst3=d);target[b]=target[c]=target[d]=init[a];oracle=[Action('READ',a),Action('WRITE',b,value=init[a]),Action('WRITE',c,value=init[a]),Action('WRITE',d,value=init[a]),Action('DONE')];args=(a,b,c,d)
    else:a,b,c,d=ks[:4];p.update(src=a,mid1=b,mid2=c,dst=d);target[b]=target[c]=target[d]=init[a];oracle=[Action('READ',a),Action('WRITE',b,value=init[a]),Action('WRITE',c,value=init[a]),Action('WRITE',d,value=init[a]),Action('DONE')];args=(a,b,c,d)
    return Task(kind,args,init,p,'REQUEST '+json.dumps(p,separators=(',',':'),sort_keys=True),target,oracle)

def emit_obj(a):
    o={'tool':a.tool}
    if a.tool=='READPAIR':
        if a.k1!=NONE:o['key1']=a.k1
        if a.k2!=NONE:o['key2']=a.k2
    else:
        if a.k1!=NONE:o['key']=a.k1
        if a.k2!=NONE:o['key2']=a.k2
    if a.value>=0:o['value']=a.value
    return o
def emit_json(a):return json.dumps(emit_obj(a),separators=(',',':'),sort_keys=True)
def ok_write(k,v):return 'RESULT '+json.dumps({'key':k,'status':'ok','tool':'WRITE','value':v},separators=(',',':'),sort_keys=True)
def ok_clear(k):return 'RESULT '+json.dumps({'key':k,'status':'ok','tool':'CLEAR'},separators=(',',':'),sort_keys=True)
def result_line(cid,v,cell,style):
    if cell.normalization:
        o={'value':v};
        if cell.provenance:o['call_id']=cid
    else:
        if style==0:o={'data':{'value':f'{v:02d}'}}
        elif style==1:o={'result':{'number':v,'unit':'register_value'}}
        else:o={'payload':[v]}
        if cell.provenance:o[{0:'id',1:'request',2:'call'}[style]]=cid
    return 'RESULT '+json.dumps(o,separators=(',',':'),sort_keys=True)

def parse_result_event(o,call_key):
    # Return (value_code 0..39, key or None). canonical uses 0..9; raw styles use 10..39.
    if not isinstance(o,dict):return None,None
    if 'value' in o and isinstance(o.get('value'),int):
        return o['value'], call_key.get(o.get('call_id')) if 'call_id' in o else None
    if isinstance(o.get('data'),dict) and 'value' in o['data']:
        try:v=int(o['data']['value'])
        except:return None,None
        return 10+v, call_key.get(o.get('id')) if 'id' in o else None
    if isinstance(o.get('result'),dict) and isinstance(o['result'].get('number'),int):
        return 20+o['result']['number'], call_key.get(o.get('request')) if 'request' in o else None
    if isinstance(o.get('payload'),list) and o['payload'] and isinstance(o['payload'][0],int):
        return 30+o['payload'][0], call_key.get(o.get('call')) if 'call' in o else None
    return None,None

# Symmetric result-event slots: normalization changes value code only; provenance adds labels only.
KIND_OFF=0;ROLE_OFF=KIND_OFF+len(KINDS);ROLE_W=len(ROLE_FIELDS)*len(KEYS)
RES_OFF=ROLE_OFF+ROLE_W;RES_SLOTS=4;VALCODE_W=41;PROV_W=9;MATCH_W=len(ROLE_FIELDS);RES_SLOT_W=VALCODE_W+PROV_W+MATCH_W;RES_W=RES_SLOTS*RES_SLOT_W
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
            code,key=parse_result_event(o,call_key)
            if code is not None:events.append((code,key))
        elif line.startswith('ACTION '):
            try:o=json.loads(line[7:]);tool=o.get('tool',NONE);k1=o.get('key',o.get('key1',NONE));k2=o.get('key2',NONE);val=o.get('value',-1);acts.append((tool,k1,k2,val));counts[tool]=counts.get(tool,0)+1
            except:pass
        elif line.startswith('SCHEMA_ERROR'):schema=1
        elif line.startswith('VERIFY_FAIL '):
            vf=1
            try:verify=json.loads(line[12:])
            except:pass
    if request:
        k=request.get('task','').upper();
        if k in KINDS:f[KIND_OFF+KINDS.index(k)]=1
        for ri,r in enumerate(ROLE_FIELDS):
            v=request.get(r)
            if v in KEYS:f[ROLE_OFF+ri*len(KEYS)+KEYS.index(v)]=1
    ev=events[-RES_SLOTS:][::-1]
    for j in range(RES_SLOTS):
        base=RES_OFF+j*RES_SLOT_W
        if j<len(ev):
            code,key=ev[j];f[base+code]=1
            pk=0 if key not in KEYS else KEYS.index(key)+1;f[base+VALCODE_W+pk]=1
            if request and key in KEYS:
                for ri,r in enumerate(ROLE_FIELDS):
                    if request.get(r)==key:f[base+VALCODE_W+PROV_W+ri]=1
        else:
            f[base+40]=1;f[base+VALCODE_W]=1
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

def style_for(seed,ci):
    return random.Random(seed*1000003 + ci*9176 + 12345).randrange(3)

def append_exec(lines,world,a,ctr,rng,cell,seed):
    lines.append('ACTION '+emit_json(a))
    if a.tool=='READ':
        ctr+=1;cid=f'c{ctr}';wire=json.dumps({'id':cid,'tool':'READ','key':a.k1},separators=(',',':'),sort_keys=True);lines.append('CALL '+wire);v=world[a.k1];lines.append(result_line(cid,v,cell,style_for(seed,ctr)))
    elif a.tool=='READPAIR':
        calls=[]
        for k in (a.k1,a.k2):
            ctr+=1;cid=f'c{ctr}';wire=json.dumps({'id':cid,'tool':'READ','key':k},separators=(',',':'),sort_keys=True);lines.append('CALL '+wire);calls.append((cid,k,world[k],ctr))
        rng.shuffle(calls)
        for cid,k,v,ci in calls:lines.append(result_line(cid,v,cell,style_for(seed,ci)))
    elif a.tool=='WRITE':world[a.k1]=a.value;lines.append(ok_write(a.k1,a.value))
    elif a.tool=='CLEAR':world[a.k1]=0;lines.append(ok_clear(a.k1))
    return ctr

OUT='/mnt/data/tool_chain_006d_final_evidence';os.makedirs(OUT,exist_ok=True)
train_rng=random.Random(SEED+1);tasks=[make_task(train_rng) for _ in range(5000)]
X=[];Y=[[],[],[],[]];TI={t:i for i,t in enumerate(TOOLS)};KC=[NONE]+KEYS;KI={k:i for i,k in enumerate(KC)};VC=[-1]+VALS;VI={v:i for i,v in enumerate(VC)}
for ti,t in enumerate(tasks):
    for ci,cell in enumerate(CELLS):
        rr=random.Random(SEED+100000+ti*13+ci);lines=[t.request];w=t.init.copy();ctr=0
        for a in t.oracle:
            X.append(features(lines));Y[0].append(TI[a.tool]);Y[1].append(KI[a.k1]);Y[2].append(KI[a.k2]);Y[3].append(VI[a.value])
            if a.tool=='DONE':break
            ctr=append_exec(lines,w,a,ctr,rr,cell,ti)
X=np.stack(X);models=[]
for h,y in enumerate(Y):
    y=np.asarray(y,dtype=np.int16);m=DecisionTreeClassifier(random_state=SEED+h,min_samples_leaf=1);m.fit(X,y);models.append(m);print('fit',h,len(y),len(m.classes_),flush=True)
with open(OUT+'/policy.pkl','wb') as f:pickle.dump({'models':models,'seed':SEED,'D':D,'KC':KC,'VC':VC},f)
sha=hashlib.sha256(open(OUT+'/policy.pkl','rb').read()).hexdigest()
json.dump({'seed':SEED,'train_tasks':len(tasks),'train_decisions':len(X),'D':D,'sha256':sha},open(OUT+'/training_summary.json','w'),indent=2)
print('DONE',json.dumps({'D':D,'n':len(X),'sha':sha}),flush=True)
