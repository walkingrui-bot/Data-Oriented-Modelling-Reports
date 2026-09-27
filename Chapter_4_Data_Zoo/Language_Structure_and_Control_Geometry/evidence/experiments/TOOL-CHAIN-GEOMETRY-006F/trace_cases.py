import json,random
src=open('/mnt/data/tool_chain_006f_formal_fast.py').read();prefix=src.split('rows=[];traces=[];task_cache={}')[0];ns={};exec(prefix,ns)
make_task=ns['make_task'];CELLS=ns['CELLS'];SEED_D=ns['SEED_D'];run=ns['run']
want=[(1,31,'provenance'),(1,9,'normalization')]
out={}
for panel,tid,label in want:
 pseed=[SEED_D+50000,SEED_D+60000,SEED_D+70000][panel-1];rr=random.Random(pseed);tasks=[make_task(rr) for _ in range(200)];t=tasks[tid]
 out[label]={'panel':panel,'task_id':tid,'kind':t.kind,'request':t.request,'init':t.init,'target':t.target,'oracle':[ns['emit_json'](a) for a in t.oracle],'conditions':{}}
 for c in CELLS:
  r=run(t,c,pseed+100000+tid);out[label]['conditions'][c.name]={'ok':r['ok'],'first_div':r['first_div'],'planner_errors':r['planner_errors'],'trace':r['trace'],'generation':r['genlog']}
json.dump(out,open('/mnt/data/tool_chain_006f_evidence/case_traces.json','w'),indent=2);print(json.dumps(out,indent=2))
