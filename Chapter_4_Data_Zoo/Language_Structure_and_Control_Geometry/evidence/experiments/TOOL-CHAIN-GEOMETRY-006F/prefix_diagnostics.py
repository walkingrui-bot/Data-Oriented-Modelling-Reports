import importlib.util, torch, random, json, csv, numpy as np
from collections import defaultdict
spec=importlib.util.spec_from_file_location('tp','/mnt/data/tool_chain_006f_train_pilot.py');tp=importlib.util.module_from_spec(spec);spec.loader.exec_module(tp)
SEED=26092931;SEED_D=26092821
z=torch.load('/mnt/data/tool_chain_006f_evidence/planner.pt',map_location='cpu');m=tp.GenPlanner(z['D'],len(z['vocab']),z['emb'],z['ctx'],z['hid']);m.load_state_dict(z['state']);m.eval()
# collect exact oracle-prefix contexts on the same 600 formal tasks x 4 cells
X=[];meta=[]
for pi,pseed in enumerate([SEED_D+50000,SEED_D+60000,SEED_D+70000],1):
    rr=random.Random(pseed);tasks=[tp.make_task(rr) for _ in range(200)]
    for ti,t in enumerate(tasks):
        amb='multi_read' if any(a.tool=='READPAIR' for a in t.oracle) or sum(a.tool=='READ' for a in t.oracle)>1 else 'single_read'
        for ci,cell in enumerate(tp.CELLS):
            rng=random.Random(pseed+900000+ti);lines=[t.request];w=t.init.copy();ctr=0
            for si,a in enumerate(t.oracle):
                X.append(tp.features(lines));meta.append({'panel':pi,'task_id':ti,'kind':t.kind,'ambiguity':amb,'condition':cell.name,'step':si+1,'oracle_tool':a.tool,'oracle_k1':a.k1,'oracle_k2':a.k2,'oracle_value':a.value,'after_result':int(si>0 and t.oracle[si-1].tool in ('READ','READPAIR'))})
                if a.tool=='DONE':break
                ctr=tp.append_exec(lines,w,a,ctr,rng,cell,ti)
X=np.stack(X).astype('float32')
# batched greedy decode 4 semantic slots
outs=[]
with torch.no_grad():
    for st in range(0,len(X),2048):
        xb=torch.tensor(X[st:st+2048]);c,h=m.start(xb);cur=torch.full((len(xb),1),tp.stoi['<BOS>'],dtype=torch.long);ids=[]
        for _ in range(4):
            log,h=m.step(cur,c,h);ii=log.argmax(-1);ids.append(ii.cpu().numpy());cur=ii[:,None]
        arr=np.stack(ids,axis=1)
        for row in arr:
            a,err=tp.seq_action(row.tolist());outs.append((a,err,[tp.VOCAB[i] for i in row]))
rows=[]
for md,(a,err,toks) in zip(meta,outs):
    exact=int(err is None and a.tup()==(md['oracle_tool'],md['oracle_k1'],md['oracle_k2'],md['oracle_value']))
    rows.append({**md,'pred_tokens':' '.join(toks),'valid':int(err is None),'exact':exact,'tool_ok':int(err is None and a.tool==md['oracle_tool']),'k1_ok':int(err is None and a.k1==md['oracle_k1']),'k2_ok':int(err is None and a.k2==md['oracle_k2']),'value_ok':int(err is None and a.value==md['oracle_value'])})
with open('/mnt/data/tool_chain_006f_evidence/prefix_diagnostics.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def agg(q):
    return {'n':len(q),'exact':sum(r['exact'] for r in q)/len(q),'tool':sum(r['tool_ok'] for r in q)/len(q),'k1':sum(r['k1_ok'] for r in q)/len(q),'k2':sum(r['k2_ok'] for r in q)/len(q),'value':sum(r['value_ok'] for r in q)/len(q)}
res={'all':agg(rows),'by_cell':{},'after_result':{},'write_only':{},'multi_read_write':{}}
for c in [x.name for x in tp.CELLS]:
    res['by_cell'][c]=agg([r for r in rows if r['condition']==c])
    res['after_result'][c]=agg([r for r in rows if r['condition']==c and r['after_result']])
    res['write_only'][c]=agg([r for r in rows if r['condition']==c and r['oracle_tool']=='WRITE'])
    res['multi_read_write'][c]=agg([r for r in rows if r['condition']==c and r['oracle_tool']=='WRITE' and r['ambiguity']=='multi_read'])
json.dump(res,open('/mnt/data/tool_chain_006f_evidence/prefix_diagnostics.json','w'),indent=2);print(json.dumps(res,indent=2))
