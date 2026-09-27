import json,random,torch,numpy as np
p='/mnt/data/tool_chain_006e_train_semantic.py';s=open(p).read();pre=s.split('X,Y,L,vocab,stoi,cnt=build()')[0];ns={};exec(pre,ns)
Model=ns['Model'];D=ns['D'];features=ns['features'];emit_json=ns['emit_json'];append_exec=ns['append_exec'];make_task=ns['make_task'];CELLS=ns['CELLS'];TOOLS=ns['TOOLS'];KEYS=ns['KEYS'];VALS=ns['VALS'];Action=ns['Action'];NONE=ns['NONE']
z=torch.load('/mnt/data/tool_chain_006e_sem_evidence/policy.pt',map_location='cpu');v=z['vocab'];stoi={t:i for i,t in enumerate(v)};m=Model(z['D'],len(v),z['emb'],z['ctx'],z['hid']);m.load_state_dict(z['state']);m.eval()
@torch.no_grad()
def gen(lines,maxn=24):
 x=torch.tensor(features(lines)[None,:],dtype=torch.float32);c,h=m.start(x);cur=torch.tensor([[stoi['<BOS>']]]);out=[]
 for _ in range(maxn):
  log,h=m.step(cur,c,h);i=int(log.argmax(-1));t=v[i]
  if t=='<EOS>':break
  if t in ('<PAD>','<BOS>'):break
  out.append(t);cur=torch.tensor([[i]])
 return ''.join(out)
def valid(o):
 if not isinstance(o,dict) or o.get('tool') not in TOOLS:return False
 t=o['tool']
 if t=='READ':return set(o)=={'tool','key'} and o.get('key') in KEYS
 if t=='READPAIR':return set(o)=={'tool','key1','key2'} and o.get('key1') in KEYS and o.get('key2') in KEYS and o['key1']!=o['key2']
 if t=='WRITE':return set(o)=={'tool','key','value'} and o.get('key') in KEYS and isinstance(o.get('value'),int) and o['value'] in VALS
 if t=='CLEAR':return set(o)=={'tool','key'} and o.get('key') in KEYS
 return set(o)=={'tool'}
rr=random.Random(9901);n=ex=jp=sv=0;first=[]
for ti in range(120):
 t=make_task(rr);c=CELLS[ti%4];rng=random.Random(8800+ti);lines=[t.request];w=t.init.copy();ctr=0
 for a in t.oracle:
  txt=gen(lines);n+=1;ex+=txt==emit_json(a)
  try:o=json.loads(txt);jp+=1;sv+=valid(o)
  except:pass
  if len(first)<12:first.append((t.kind,emit_json(a),txt))
  if a.tool=='DONE':break
  ctr=append_exec(lines,w,a,ctr,rng,c,ti)
print(json.dumps({'n':n,'exact':ex/n,'json':jp/n,'schema':sv/n,'examples':first},indent=2))
