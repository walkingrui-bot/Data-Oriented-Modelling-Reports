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


OUT='/mnt/data/tool_chain_006d_final_evidence'
with open(OUT+'/policy.pkl','rb') as f:_pk=pickle.load(f)
models=_pk['models'];KC=_pk['KC'];VC=_pk['VC']
def predict(lines):
    x=features(lines).reshape(1,-1);ix=[int(m.predict(x)[0]) for m in models];return Action(TOOLS[ix[0]],KC[ix[1]],KC[ix[2]],VC[ix[3]])
def valid_action(a):
    if a.tool=='READ':return a.k1 in KEYS and a.k2==NONE and a.value==-1
    if a.tool=='READPAIR':return a.k1 in KEYS and a.k2 in KEYS and a.k1!=a.k2 and a.value==-1
    if a.tool=='WRITE':return a.k1 in KEYS and a.k2==NONE and a.value in VALS
    if a.tool=='CLEAR':return a.k1 in KEYS and a.k2==NONE and a.value==-1
    if a.tool=='DONE':return a.k1==NONE and a.k2==NONE and a.value==-1
    return False

def run(t,cell,seed,max_steps=14):
    rr=random.Random(seed);w=t.init.copy();lines=[t.request];ctr=0;oi=0;fd=0;schema=0;wrong_done=0;vf=0;recovered=0
    for step in range(max_steps):
        a=predict(lines)
        if not fd and a.tup()!=t.oracle[min(oi,len(t.oracle)-1)].tup():fd=step+1
        if not valid_action(a):
            schema+=1;lines.append('ACTION '+emit_json(a));lines.append('SCHEMA_ERROR '+json.dumps({'error':'invalid_tool_arguments'},separators=(',',':')));continue
        oi+=1
        if a.tool in ('READ','READPAIR','WRITE','CLEAR'):ctr=append_exec(lines,w,a,ctr,rr,cell,seed+step)
        else:
            lines.append('ACTION '+emit_json(a))
            if w==t.target:
                lines.append('VERIFY_OK');return {'ok':1,'steps':step+1,'first_div':fd,'schema_errors':schema,'wrong_done':wrong_done,'verify_failures':vf,'recovered':recovered,'trace':lines,'world':w}
            wrong_done=1;vf+=1;diff={k:{'expected':t.target[k],'observed':w[k]} for k in KEYS if w[k]!=t.target[k]};lines.append('STATE '+json.dumps(w,separators=(',',':'),sort_keys=True));lines.append('VERIFY_FAIL '+json.dumps(diff,separators=(',',':'),sort_keys=True))
            if vf>=2:break
    return {'ok':int(w==t.target),'steps':max_steps,'first_div':fd,'schema_errors':schema,'wrong_done':wrong_done,'verify_failures':vf,'recovered':int(wrong_done and w==t.target),'trace':lines,'world':w}

def prefix_acc(tasks,cell):
    n=exact=0;parts=[0,0,0,0]
    for ti,t in enumerate(tasks):
        rr=random.Random(SEED+900000+ti);lines=[t.request];w=t.init.copy();ctr=0
        for a in t.oracle:
            p=predict(lines);n+=1;exact+=p.tup()==a.tup();parts[0]+=p.tool==a.tool;parts[1]+=p.k1==a.k1;parts[2]+=p.k2==a.k2;parts[3]+=p.value==a.value
            if a.tool=='DONE':break
            ctr=append_exec(lines,w,a,ctr,rr,cell,ti)
    return {'n':n,'exact':exact/n,'tool':parts[0]/n,'k1':parts[1]/n,'k2':parts[2]/n,'value':parts[3]/n}

def unit_factorial(units):
    def m(n):return sum(u[n] for u in units)/len(units)
    a,b,c,d=m('P1_N1'),m('P1_N0'),m('P0_N1'),m('P0_N0')
    return {'P1_N1':a,'P1_N0':b,'P0_N1':c,'P0_N0':d,'provenance_main_pp':100*((a+b-c-d)/2),'normalization_main_pp':100*((a+c-b-d)/2),'interaction_pp':100*((a-c)-(b-d))}
def boot_units(units,B=2500,seed=1):
    rr=random.Random(seed);n=len(units);ks=['provenance_main_pp','normalization_main_pp','interaction_pp'];v={k:[] for k in ks}
    for _ in range(B):
        s=[units[rr.randrange(n)] for __ in range(n)];st=unit_factorial(s)
        for k in ks:v[k].append(st[k])
    out={}
    for k,a in v.items():a.sort();out[k]=[a[int(.025*B)],a[int(.975*B)]]
    return out

allrows=[];panels=[];task_cache={}
for pi,pseed in enumerate([SEED+50000,SEED+60000,SEED+70000],1):
    rr=random.Random(pseed);tasks=[make_task(rr) for _ in range(200)];task_cache[pi]=tasks;summ={};pref={}
    for cell in CELLS:
        pref[cell.name]=prefix_acc(tasks,cell);rs=[]
        for i,t in enumerate(tasks):
            r=run(t,cell,pseed+100000+i);rs.append(r);amb='multi_read' if any(a.tool=='READPAIR' for a in t.oracle) or sum(a.tool=='READ' for a in t.oracle)>1 else 'single_read'
            allrows.append({'panel':pi,'task_id':i,'kind':t.kind,'ambiguity':amb,'oracle_len':len(t.oracle),'condition':cell.name,'provenance':int(cell.provenance),'normalization':int(cell.normalization),'ok':r['ok'],'steps':r['steps'],'first_div':r['first_div'],'schema_errors':r['schema_errors'],'wrong_done':r['wrong_done'],'verify_failures':r['verify_failures'],'recovered':r['recovered']})
        failfd=[x['first_div'] for x in rs if not x['ok'] and x['first_div']]
        summ[cell.name]={'accuracy':sum(x['ok'] for x in rs)/len(rs),'wrong_done_rate':sum(x['wrong_done'] for x in rs)/len(rs),'mean_steps':sum(x['steps'] for x in rs)/len(rs),'mean_first_div_failure':sum(failfd)/len(failfd) if failfd else None}
    panels.append({'panel':pi,'seed':pseed,'prefix_accuracy':pref,'summaries':summ});print('panel',pi,summ,flush=True)

by={}
for r in allrows:by.setdefault((r['panel'],r['task_id']),{})[r['condition']]=r
units=[]
for (p,i),z in by.items():
    t=task_cache[p][i];amb='multi_read' if any(a.tool=='READPAIR' for a in t.oracle) or sum(a.tool=='READ' for a in t.oracle)>1 else 'single_read'
    units.append({'panel':p,'task_id':i,'kind':t.kind,'ambiguity':amb,**{c.name:z[c.name]['ok'] for c in CELLS}})
pooled=unit_factorial(units);ci=boot_units(units,2500,SEED+99)
sub={}
for amb in ['single_read','multi_read']:
    uu=[u for u in units if u['ambiguity']==amb];sub[amb]={'n':len(uu),**unit_factorial(uu),'bootstrap95':boot_units(uu,1500,SEED+(1 if amb=='single_read' else 2))}
family={}
for kind in KINDS:
    uu=[u for u in units if u['kind']==kind]
    if uu:family[kind]={'n':len(uu),**unit_factorial(uu)}
fd={}
for c in CELLS:
    a=[r['first_div'] for r in allrows if r['condition']==c.name and not r['ok'] and r['first_div']]
    fd[c.name]={'n_fail_div':len(a),'mean':sum(a)/len(a) if a else None,'median':float(np.median(a)) if a else None}
reps={}
for u in units:
    if u['P1_N1'] and u['P1_N0'] and (not u['P0_N1']) and (not u['P0_N0']):
        p,i=u['panel'],u['task_id'];t=task_cache[p][i];pseed=[SEED+50000,SEED+60000,SEED+70000][p-1];reps['provenance']={'panel':p,'task_id':i,'kind':t.kind,'request':t.request,'init':t.init,'target':t.target,'traces':{c.name:run(t,c,pseed+100000+i)['trace'] for c in CELLS}};break
for u in units:
    if u['P1_N1'] and u['P0_N1'] and (not u['P1_N0']) and (not u['P0_N0']):
        p,i=u['panel'],u['task_id'];t=task_cache[p][i];pseed=[SEED+50000,SEED+60000,SEED+70000][p-1];reps['normalization']={'panel':p,'task_id':i,'kind':t.kind,'request':t.request,'init':t.init,'target':t.target,'traces':{c.name:run(t,c,pseed+100000+i)['trace'] for c in CELLS}};break
sha=hashlib.sha256(open(OUT+'/policy.pkl','rb').read()).hexdigest();train=json.load(open(OUT+'/training_summary.json'))
res={'experiment':'TOOL-CHAIN-GEOMETRY-006D','design':'symmetry-controlled 2x2 provenance x normalization factorial with identity-independent raw-style assignment','seed':SEED,'model':{'family':'DecisionTree structured event-slot policy, four independent action heads','feature_dim':D,'train_tasks':train['train_tasks'],'train_decisions':train['train_decisions'],'policy_sha256':sha},'factorial':{'provenance':'result event carries explicit call-derived key label vs unlabeled','normalization':'canonical numeric value code vs backend-specific style-preserving raw value code','value_visibility':'all four cells expose the observed value in the same event slot; factors change label/code only','raw_style_assignment':'backend raw style varies independently across episodes/calls and is not a deterministic call-index code'},'panels':panels,'pooled':pooled,'bootstrap95':ci,'ambiguity_subgroups':sub,'task_family':family,'first_divergence_failures':fd,'representative_cases':reps}
json.dump(res,open(OUT+'/results.json','w'),indent=2)
import csv
with open(OUT+'/episode_summary.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
with open(OUT+'/paired_task_outcomes.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(units[0]));w.writeheader();w.writerows(units)
json.dump({'experiment':'TOOL-CHAIN-GEOMETRY-006D','script':'tool_chain_006d_final_eval.py','seed':SEED,'policy_sha256':sha,'note':'Final symmetry-controlled run. Raw style assignment is independent of call identity; all four interface cells included in training before freeze; three held-out 200-task panels share one frozen policy.'},open(OUT+'/source_manifest.json','w'),indent=2)
print('FINAL',json.dumps({'pooled':pooled,'ci':ci,'sub':sub,'fd':fd}),flush=True)
