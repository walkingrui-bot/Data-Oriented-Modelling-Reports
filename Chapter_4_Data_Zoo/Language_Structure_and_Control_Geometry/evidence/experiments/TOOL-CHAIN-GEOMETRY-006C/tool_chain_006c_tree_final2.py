import os, json, random, math, hashlib, csv, re, pickle
from dataclasses import dataclass
from collections import defaultdict
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from jsonschema import Draft202012Validator

SEED=26092761
random.seed(SEED); np.random.seed(SEED)
KEYS=list('ABCDEFGH'); VALS=list(range(10)); NONE='<NONE>'
TOOLS=['READ','READPAIR','WRITE','CLEAR','DONE']; KINDS=['COPY','BACKUP_CLEAR','SWAP','DUAL_COPY','ROTATE3','DUPLICATE','MOVE2','FANOUT3','CHAIN_COPY']
ROLE_FIELDS=['src','dst','a','b','c','src1','dst1','src2','dst2','dst3','mid1','mid2']

@dataclass(frozen=True)
class Action:
    tool:str; k1:str=NONE; k2:str=NONE; value:int=-1
    def tup(self): return (self.tool,self.k1,self.k2,self.value)
@dataclass
class Task:
    kind:str; args:tuple; init:dict; payload:dict; request:str; target:dict; oracle:list

def make_task(rng,force_kind=None):
    init={k:rng.randrange(10) for k in KEYS};ks=rng.sample(KEYS,8);kind=force_kind or rng.choice(KINDS);target=init.copy();p={'task':kind.lower()}
    if kind=='COPY':
        s,d=ks[:2];p.update(src=s,dst=d);target[d]=init[s];oracle=[Action('READ',s),Action('WRITE',d,value=init[s]),Action('DONE')];args=(s,d)
    elif kind=='BACKUP_CLEAR':
        s,d=ks[:2];p.update(src=s,dst=d);target[d]=init[s];target[s]=0;oracle=[Action('READ',s),Action('WRITE',d,value=init[s]),Action('CLEAR',s),Action('DONE')];args=(s,d)
    elif kind=='SWAP':
        a,b=ks[:2];p.update(a=a,b=b);target[a],target[b]=init[b],init[a];oracle=[Action('READPAIR',a,b),Action('WRITE',a,value=init[b]),Action('WRITE',b,value=init[a]),Action('DONE')];args=(a,b)
    elif kind=='DUAL_COPY':
        a,b,c,d=ks[:4];p.update(src1=a,dst1=c,src2=b,dst2=d);target[c]=init[a];target[d]=init[b];oracle=[Action('READPAIR',a,b),Action('WRITE',c,value=init[a]),Action('WRITE',d,value=init[b]),Action('DONE')];args=(a,b,c,d)
    elif kind=='ROTATE3':
        a,b,c=ks[:3];p.update(a=a,b=b,c=c);target[b]=init[a];target[c]=init[b];target[a]=init[c];oracle=[Action('READPAIR',a,b),Action('READ',c),Action('WRITE',b,value=init[a]),Action('WRITE',c,value=init[b]),Action('WRITE',a,value=init[c]),Action('DONE')];args=(a,b,c)
    elif kind=='DUPLICATE':
        a,b,c=ks[:3];p.update(src=a,dst1=b,dst2=c);target[b]=target[c]=init[a];oracle=[Action('READ',a),Action('WRITE',b,value=init[a]),Action('WRITE',c,value=init[a]),Action('DONE')];args=(a,b,c)
    elif kind=='MOVE2':
        a,b,c,d=ks[:4];p.update(src1=a,dst1=c,src2=b,dst2=d);target[c]=init[a];target[d]=init[b];target[a]=0;target[b]=0;oracle=[Action('READPAIR',a,b),Action('WRITE',c,value=init[a]),Action('WRITE',d,value=init[b]),Action('CLEAR',a),Action('CLEAR',b),Action('DONE')];args=(a,b,c,d)
    elif kind=='FANOUT3':
        a,b,c,d=ks[:4];p.update(src=a,dst1=b,dst2=c,dst3=d);target[b]=target[c]=target[d]=init[a];oracle=[Action('READ',a),Action('WRITE',b,value=init[a]),Action('WRITE',c,value=init[a]),Action('WRITE',d,value=init[a]),Action('DONE')];args=(a,b,c,d)
    else:
        a,b,c,d=ks[:4];p.update(src=a,mid1=b,mid2=c,dst=d);target[b]=target[c]=target[d]=init[a];oracle=[Action('READ',a),Action('WRITE',b,value=init[a]),Action('WRITE',c,value=init[a]),Action('WRITE',d,value=init[a]),Action('DONE')];args=(a,b,c,d)
    request='REQUEST '+json.dumps(p,separators=(',',':'),sort_keys=True);return Task(kind,args,init,p,request,target,oracle)

SCHEMAS={
 'READ':{'type':'object','properties':{'tool':{'const':'READ'},'key':{'enum':KEYS}},'required':['tool','key'],'additionalProperties':False},
 'READPAIR':{'type':'object','properties':{'tool':{'const':'READPAIR'},'key1':{'enum':KEYS},'key2':{'enum':KEYS}},'required':['tool','key1','key2'],'additionalProperties':False},
 'WRITE':{'type':'object','properties':{'tool':{'const':'WRITE'},'key':{'enum':KEYS},'value':{'type':'integer','minimum':0,'maximum':9}},'required':['tool','key','value'],'additionalProperties':False},
 'CLEAR':{'type':'object','properties':{'tool':{'const':'CLEAR'},'key':{'enum':KEYS}},'required':['tool','key'],'additionalProperties':False},
 'DONE':{'type':'object','properties':{'tool':{'const':'DONE'}},'required':['tool'],'additionalProperties':False}}
VALID={k:Draft202012Validator(v) for k,v in SCHEMAS.items()}

def emit_obj(a):
    # Preserve independent-head extras so schema strictness is genuinely testable.
    obj={'tool':a.tool}
    if a.tool=='READPAIR':
        if a.k1!=NONE:obj['key1']=a.k1
        if a.k2!=NONE:obj['key2']=a.k2
    else:
        if a.k1!=NONE:obj['key']=a.k1
        if a.k2!=NONE:obj['key2']=a.k2
    if a.value>=0:obj['value']=a.value
    return obj

def emit_json(a): return json.dumps(emit_obj(a),separators=(',',':'),sort_keys=True)
def valid_obj(obj):
    if not isinstance(obj,dict) or obj.get('tool') not in VALID:return False
    if not VALID[obj['tool']].is_valid(obj):return False
    if obj.get('tool')=='READPAIR' and obj.get('key1')==obj.get('key2'):return False
    return True

def coerce(a,t):
    mentions=list(t.args);k1=a.k1 if a.k1 in KEYS else mentions[0];k2=a.k2 if a.k2 in KEYS and a.k2!=k1 else next((k for k in mentions if k!=k1),'B');val=a.value if a.value in VALS else 0
    if a.tool=='READ':return Action('READ',k1)
    if a.tool=='READPAIR':return Action('READPAIR',k1,k2)
    if a.tool=='WRITE':return Action('WRITE',k1,value=val)
    if a.tool=='CLEAR':return Action('CLEAR',k1)
    return Action('DONE')

def canonical_result(cid,v):return 'RESULT '+json.dumps({'call_id':cid,'value':v},separators=(',',':'),sort_keys=True)
def raw_result(cid,v,style):
    if style==0:o={'id':cid,'data':{'value':f'{v:02d}'}}
    elif style==1:o={'request':cid,'result':{'number':v,'unit':'register_value'}}
    else:o={'call':cid,'payload':[v]}
    return 'RESULT '+json.dumps(o,separators=(',',':'),sort_keys=True)
def ok_write(k,v):return 'RESULT '+json.dumps({'key':k,'status':'ok','tool':'WRITE','value':v},separators=(',',':'),sort_keys=True)
def ok_clear(k):return 'RESULT '+json.dumps({'key':k,'status':'ok','tool':'CLEAR'},separators=(',',':'),sort_keys=True)

# Feature layout helpers.
KIND_OFF=0;ROLE_OFF=KIND_OFF+len(KINDS);ROLE_W=len(ROLE_FIELDS)*len(KEYS);BOUND_OFF=ROLE_OFF+ROLE_W;BOUND_W=len(KEYS)*11
UNBOUND_OFF=BOUND_OFF+BOUND_W;UNBOUND_W=4*11
LASTACT_OFF=UNBOUND_OFF+UNBOUND_W;LASTACT_W=3*(len(TOOLS)+len(KEYS)+len(KEYS)+11)
COUNT_OFF=LASTACT_OFF+LASTACT_W;COUNT_W=len(TOOLS)+1
VERIFY_OFF=COUNT_OFF+COUNT_W;VERIFY_W=len(KEYS)*11+2
D=VERIFY_OFF+VERIFY_W

def onehot_value(x,unknown_index=True):
    # 0=unknown, 1..10=value 0..9
    return 0 if x is None else x+1

def features(lines):
    f=np.zeros(D,dtype=np.float32)
    request=None;call_key={};bound={};unbound=[];acts=[];tool_counts={t:0 for t in TOOLS};schema_err=0;verify=None;verify_flag=0
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
            # canonical call-result binding only; raw backend shapes require adapter normalization.
            if isinstance(o,dict) and 'call_id' in o and 'value' in o:
                k=call_key.get(o['call_id']);
                if k in KEYS and isinstance(o['value'],int):bound[k]=o['value']
            elif isinstance(o,dict) and set(o.keys())=={'value'} and isinstance(o['value'],int):unbound.append(o['value'])
        elif line.startswith('ACTION '):
            try:o=json.loads(line[7:]);tool=o.get('tool',NONE);k1=o.get('key',o.get('key1',NONE));k2=o.get('key2',NONE);val=o.get('value',-1);acts.append((tool,k1,k2,val));tool_counts[tool]=tool_counts.get(tool,0)+1
            except:pass
        elif line.startswith('SCHEMA_ERROR'):schema_err=1
        elif line.startswith('VERIFY_FAIL '):
            verify_flag=1
            try:verify=json.loads(line[12:])
            except:verify=None
    if request:
        k=request.get('task','').upper();
        if k in KINDS:f[KIND_OFF+KINDS.index(k)]=1
        for ri,r in enumerate(ROLE_FIELDS):
            v=request.get(r)
            if v in KEYS:f[ROLE_OFF+ri*len(KEYS)+KEYS.index(v)]=1
    for ki,k in enumerate(KEYS):
        ix=onehot_value(bound.get(k));f[BOUND_OFF+ki*11+ix]=1
    for j in range(4):
        v=unbound[-4+j] if len(unbound)>=4-j else None;f[UNBOUND_OFF+j*11+onehot_value(v)]=1
    for j,a in enumerate(acts[-3:][::-1]):
        tool,k1,k2,val=a;base=LASTACT_OFF+j*(len(TOOLS)+len(KEYS)+len(KEYS)+11)
        if tool in TOOLS:f[base+TOOLS.index(tool)]=1
        if k1 in KEYS:f[base+len(TOOLS)+KEYS.index(k1)]=1
        if k2 in KEYS:f[base+len(TOOLS)+len(KEYS)+KEYS.index(k2)]=1
        f[base+len(TOOLS)+2*len(KEYS)+onehot_value(val if isinstance(val,int) and 0<=val<=9 else None)]=1
    for ti,t in enumerate(TOOLS):f[COUNT_OFF+ti]=min(tool_counts.get(t,0),6)/6
    f[COUNT_OFF+len(TOOLS)]=schema_err
    if verify:
        for ki,k in enumerate(KEYS):
            exp=None
            if k in verify and isinstance(verify[k],dict):exp=verify[k].get('expected')
            f[VERIFY_OFF+ki*11+onehot_value(exp if isinstance(exp,int) else None)]=1
    f[VERIFY_OFF+len(KEYS)*11]=verify_flag;f[VERIFY_OFF+len(KEYS)*11+1]=1 if verify_flag and verify else 0
    return f

def append_exec(lines,world,a,ctr,rng,parallel=True,binding=True,normalize=True,seed=0):
    # Actual call path: serialize -> parse -> execute. Caller has already schema-validated.
    lines.append('ACTION '+emit_json(a))
    if a.tool=='READ':
        ctr+=1;cid=f'c{ctr}';call={'id':cid,'tool':'READ','key':a.k1};wire=json.dumps(call,separators=(',',':'),sort_keys=True);parsed=json.loads(wire);lines.append('CALL '+wire);v=world[parsed['key']]
        if normalize:lines.append(canonical_result(cid,v) if binding else 'RESULT '+json.dumps({'value':v},separators=(',',':')))
        else:
            s=raw_result(cid,v,(seed+ctr)%3)
            if not binding:
                o=json.loads(s[7:]);o.pop('id',None);o.pop('request',None);o.pop('call',None);s='RESULT '+json.dumps(o,separators=(',',':'),sort_keys=True)
            lines.append(s)
    elif a.tool=='READPAIR':
        calls=[]
        for k in (a.k1,a.k2):
            ctr+=1;cid=f'c{ctr}';wire=json.dumps({'id':cid,'tool':'READ','key':k},separators=(',',':'),sort_keys=True);parsed=json.loads(wire);lines.append('CALL '+wire);calls.append((cid,parsed['key'],world[parsed['key']]))
        if parallel:rng.shuffle(calls)
        for cid,k,v in calls:
            if normalize:lines.append(canonical_result(cid,v) if binding else 'RESULT '+json.dumps({'value':v},separators=(',',':')))
            else:
                s=raw_result(cid,v,(seed+ctr+len(lines))%3)
                if not binding:
                    o=json.loads(s[7:]);o.pop('id',None);o.pop('request',None);o.pop('call',None);s='RESULT '+json.dumps(o,separators=(',',':'),sort_keys=True)
                lines.append(s)
    elif a.tool=='WRITE':world[a.k1]=a.value;lines.append(ok_write(a.k1,a.value))
    elif a.tool=='CLEAR':world[a.k1]=0;lines.append(ok_clear(a.k1))
    return ctr

# Generate learned-policy corpus from executable oracle trajectories.
train_rng=random.Random(SEED+1);train_tasks=[make_task(train_rng) for _ in range(12000)]
X=[];Y=[[],[],[],[]]
TI={t:i for i,t in enumerate(TOOLS)};KI={k:i for i,k in enumerate([NONE]+KEYS)};VI={v:i for i,v in enumerate([-1]+VALS)};KC=[NONE]+KEYS;VC=[-1]+VALS
for ti,t in enumerate(train_tasks):
    rng=random.Random(SEED+100000+ti);lines=[t.request];world=t.init.copy();ctr=0
    for a in t.oracle:
        X.append(features(lines));Y[0].append(TI[a.tool]);Y[1].append(KI[a.k1]);Y[2].append(KI[a.k2]);Y[3].append(VI[a.value])
        if a.tool=='DONE':break
        ctr=append_exec(lines,world,a,ctr,rng,True,True,True,ti)
    if ti%4==0:
        bad=t.target.copy();k=rng.choice(KEYS);bad[k]=(bad[k]+rng.randrange(1,10))%10;diff={kk:{'expected':t.target[kk],'observed':bad[kk]} for kk in KEYS if bad[kk]!=t.target[kk]};l2=[t.request,'STATE '+json.dumps(bad,separators=(',',':'),sort_keys=True),'VERIFY_FAIL '+json.dumps(diff,separators=(',',':'),sort_keys=True)];fix=Action('WRITE',k,value=t.target[k])
        for inp,a in [(l2,fix),(l2+['ACTION '+emit_json(fix),ok_write(k,t.target[k]),'VERIFY_OK'],Action('DONE'))]:
            X.append(features(inp));Y[0].append(TI[a.tool]);Y[1].append(KI[a.k1]);Y[2].append(KI[a.k2]);Y[3].append(VI[a.value])
    if ti%7==0:
        l=[t.request,'SCHEMA_ERROR '+json.dumps({'error':'invalid_tool_arguments'},separators=(',',':'))];a=t.oracle[0];X.append(features(l));Y[0].append(TI[a.tool]);Y[1].append(KI[a.k1]);Y[2].append(KI[a.k2]);Y[3].append(VI[a.value])
X=np.stack(X);Ys=[np.asarray(y,dtype=np.int16) for y in Y]
models=[]
for h,y in enumerate(Ys):
    m=DecisionTreeClassifier(random_state=SEED+h,min_samples_leaf=1);m.fit(X,y);models.append(m);print('fit head',h,'classes',len(m.classes_),flush=True)

def predict(lines):
    x=features(lines).reshape(1,-1);ix=[int(m.predict(x)[0]) for m in models];return Action(TOOLS[ix[0]],KC[ix[1]],KC[ix[2]],VC[ix[3]])

out='/mnt/data/tool_chain_006c_evidence';os.makedirs(out,exist_ok=True)
with open(out+'/policy.pkl','wb') as f:pickle.dump({'models':models,'seed':SEED,'feature_dim':D},f)
sha=hashlib.sha256(open(out+'/policy.pkl','rb').read()).hexdigest()

@dataclass
class Cond:
    name:str;history:str='full';binding:bool=True;dispatch:str='parallel';normalize:bool=True;strict:bool=True;verify:bool=True
CONDS=[Cond('BASE'),Cond('NO_STATE',history='last'),Cond('NO_BINDING_PARALLEL',binding=False),Cond('NO_BINDING_SEQUENTIAL',binding=False,dispatch='sequential'),Cond('RAW_JSON_NO_NORMALIZATION',normalize=False),Cond('BEST_EFFORT_SCHEMA',strict=False),Cond('NO_VERIFY',verify=False)]

def model_lines(t,lines,c):return lines if c.history=='full' else [t.request]+lines[1:][-3:]

def run(t,c,seed,max_steps=14):
    rng=random.Random(seed);world=t.init.copy();lines=[t.request];ctr=0;oi=0;first_div=0;schema=0;wrong_done=0;vf=0;recovered=0
    for step in range(max_steps):
        a=predict(model_lines(t,lines,c))
        if not first_div and a.tup()!=t.oracle[min(oi,len(t.oracle)-1)].tup():first_div=step+1
        wire=emit_json(a)
        try:o=json.loads(wire)
        except:o={}
        valid=valid_obj(o)
        if c.strict and not valid:
            schema+=1;lines.append('ACTION '+wire);lines.append('SCHEMA_ERROR '+json.dumps({'error':'invalid_tool_arguments'},separators=(',',':')));continue
        if not c.strict and not valid:a=coerce(a,t)
        oi+=1
        if a.tool in ('READ','READPAIR','WRITE','CLEAR'):ctr=append_exec(lines,world,a,ctr,rng,c.dispatch=='parallel',c.binding,c.normalize,seed+step)
        else:
            lines.append('ACTION '+emit_json(a))
            if world==t.target:
                if c.verify:lines.append('VERIFY_OK')
                return {'ok':1,'steps':step+1,'first_div':first_div,'schema_errors':schema,'wrong_done':wrong_done,'verify_failures':vf,'recovered':recovered,'trace':lines,'world':world}
            wrong_done=1
            if c.verify:
                vf+=1;diff={k:{'expected':t.target[k],'observed':world[k]} for k in KEYS if world[k]!=t.target[k]};lines.append('STATE '+json.dumps(world,separators=(',',':'),sort_keys=True));lines.append('VERIFY_FAIL '+json.dumps(diff,separators=(',',':'),sort_keys=True))
                if vf>=2:break
            else:break
    return {'ok':int(world==t.target),'steps':max_steps,'first_div':first_div,'schema_errors':schema,'wrong_done':wrong_done,'verify_failures':vf,'recovered':int(wrong_done and world==t.target),'trace':lines,'world':world}

def prefix_acc(tasks):
    n=exact=0;parts=[0,0,0,0]
    for ti,t in enumerate(tasks):
        rng=random.Random(SEED+900000+ti);lines=[t.request];w=t.init.copy();ctr=0
        for a in t.oracle:
            p=predict(lines);n+=1;exact+=p.tup()==a.tup();parts[0]+=p.tool==a.tool;parts[1]+=p.k1==a.k1;parts[2]+=p.k2==a.k2;parts[3]+=p.value==a.value
            if a.tool=='DONE':break
            ctr=append_exec(lines,w,a,ctr,rng,True,True,True,ti)
    return {'n':n,'exact':exact/n,'tool':parts[0]/n,'k1':parts[1]/n,'k2':parts[2]/n,'value':parts[3]/n}

def mcnemar(b,c):
    n=b+c
    if not n:return 1.0
    probs=[math.comb(n,i)*.5**n for i in range(n+1)];pk=probs[min(b,c)];return min(1,sum(p for p in probs if p<=pk+1e-15))
def boot(a,b,B=800,seed=1):
    rng=random.Random(seed);n=len(a);v=[]
    for _ in range(B):
        s=0
        for __ in range(n):
            i=rng.randrange(n);s+=b[i]-a[i]
        v.append(100*s/n)
    v.sort();return [v[int(.025*B)],v[int(.975*B)]]

allrows=[];panels=[];reps={};panel_tasks={}
for pi,pseed in enumerate([SEED+50000,SEED+60000,SEED+70000],1):
    rr=random.Random(pseed);tasks=[make_task(rr) for _ in range(200)];panel_tasks[pi]=tasks;pref=prefix_acc(tasks);lookup={};summ={}
    for c in CONDS:
        rs=[]
        for i,t in enumerate(tasks):
            r=run(t,c,pseed+100000+i);rs.append(r);lookup[(c.name,i)]=r['ok'];allrows.append({'panel':pi,'task_id':i,'kind':t.kind,'oracle_len':len(t.oracle),'condition':c.name,'ok':r['ok'],'steps':r['steps'],'first_div':r['first_div'],'schema_errors':r['schema_errors'],'wrong_done':r['wrong_done'],'verify_failures':r['verify_failures'],'recovered':r['recovered']})
        summ[c.name]={'accuracy':sum(x['ok'] for x in rs)/len(rs),'wrong_done_rate':sum(x['wrong_done'] for x in rs)/len(rs),'schema_error_episode_rate':sum(x['schema_errors']>0 for x in rs)/len(rs),'mean_steps':sum(x['steps'] for x in rs)/len(rs)}
    base=[lookup[('BASE',i)] for i in range(200)];comp={}
    for c in CONDS[1:]:
        arr=[lookup[(c.name,i)] for i in range(200)];bo=sum(x==1 and y==0 for x,y in zip(base,arr));co=sum(x==0 and y==1 for x,y in zip(base,arr));comp[c.name]={'delta_pp':100*(sum(arr)-sum(base))/200,'bootstrap95_pp':boot(base,arr,seed=pseed),'base_only_success':bo,'cond_only_success':co,'mcnemar_p':mcnemar(bo,co)}
        if c.name not in reps:
            for i,t in enumerate(tasks):
                if lookup[('BASE',i)] and not lookup[(c.name,i)]:reps[c.name]={'panel':pi,'task_id':i,'request':t.request,'init':t.init,'target':t.target,'baseline':run(t,CONDS[0],pseed+100000+i)['trace'],'perturbed':run(t,c,pseed+100000+i)['trace']};break
    panels.append({'panel':pi,'seed':pseed,'prefix_accuracy':pref,'summaries':summ,'comparisons_vs_baseline':comp});print('panel',pi,pref,summ,flush=True)

pooled={}
for c in CONDS:
    rr=[x for x in allrows if x['condition']==c.name];pooled[c.name]={'n':len(rr),'accuracy':sum(x['ok'] for x in rr)/len(rr),'wrong_done_rate':sum(x['wrong_done'] for x in rr)/len(rr),'schema_error_episode_rate':sum(x['schema_errors']>0 for x in rr)/len(rr),'mean_steps':sum(x['steps'] for x in rr)/len(rr)}
base=[x['ok'] for x in allrows if x['condition']=='BASE'];pcomp={}
for c in CONDS[1:]:
    arr=[x['ok'] for x in allrows if x['condition']==c.name];bo=sum(x==1 and y==0 for x,y in zip(base,arr));co=sum(x==0 and y==1 for x,y in zip(base,arr));pcomp[c.name]={'delta_pp':100*(sum(arr)-sum(base))/len(base),'bootstrap95_pp':boot(base,arr,1000,SEED+999),'base_only_success':bo,'cond_only_success':co,'mcnemar_p':mcnemar(bo,co)}
length={}
for c in CONDS:
    d={}
    for L in sorted(set(x['oracle_len'] for x in allrows)):
        rr=[x for x in allrows if x['condition']==c.name and x['oracle_len']==L];d[str(L)]=sum(x['ok'] for x in rr)/len(rr) if rr else None
    length[c.name]=d
res={'experiment':'TOOL-CHAIN-GEOMETRY-006C','seed':SEED,'model':{'family':'DecisionTree structured transcript policy, four independent action heads','feature_dim':D,'train_tasks':len(train_tasks),'train_decisions':len(X),'policy_sha256':sha,'trees_per_head':1},'typed_interface':{'serialization':'json.dumps -> json.loads','validation':'JSON Schema Draft 2020-12','action_schemas':list(SCHEMAS),'backend_raw_formats':3},'panels':panels,'pooled_summaries':pooled,'pooled_comparisons':pcomp,'chain_length_accuracy':length,'representative_cases':reps}
with open(out+'/results.json','w') as f:json.dump(res,f,indent=2)
with open(out+'/episode_summary.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
with open(out+'/source_manifest.json','w') as f:json.dump({'experiment':'TOOL-CHAIN-GEOMETRY-006C','script':'tool_chain_006c_typed_policy.py','seed':SEED,'policy_sha256':sha,'note':'All three panels use the same frozen policy; task/world seeds are independent.'},f,indent=2)
print('FINAL',json.dumps({'model':res['model'],'panels':panels,'pooled':pooled,'comparisons':pcomp,'length':length}),flush=True)
