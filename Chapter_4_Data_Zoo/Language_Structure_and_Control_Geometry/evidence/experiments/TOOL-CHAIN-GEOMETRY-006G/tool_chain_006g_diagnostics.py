import os,json,random,csv,importlib.util
from collections import defaultdict
import numpy as np, torch
OUT='/mnt/data/tool_chain_006g_evidence';SEED_D=26092821
spec=importlib.util.spec_from_file_location('g','/mnt/data/tool_chain_006g_train.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
z=torch.load(OUT+'/planner.pt',map_location='cpu');m=g.GenPlanner(z['D'],len(z['vocab']),z['emb'],z['ctx'],z['hid']);m.load_state_dict(z['state']);m.eval()
@torch.no_grad()
def plan(lines):
    x=torch.tensor(g.features(lines)[None,:],dtype=torch.float32);c,h=m.start(x);cur=torch.tensor([[g.stoi['<BOS>']]]);ids=[]
    for _ in range(4):log,h=m.step(cur,c,h);i=int(log.argmax(-1));ids.append(i);cur=torch.tensor([[i]])
    a,err=g.seq_action(ids);return a,err

def ambiguity(t):return 'multi_read' if any(a.tool=='READPAIR' for a in t.oracle) or sum(a.tool=='READ' for a in t.oracle)>1 else 'single_read'
# prefix diagnostics on exact formal panels
rows=[]
for pi,pseed in enumerate([SEED_D+50000,SEED_D+60000,SEED_D+70000],1):
    rr=random.Random(pseed);tasks=[g.make_task(rr) for _ in range(200)]
    for regime,styles in [('seen',g.SEEN_STYLES),('unseen',g.UNSEEN_STYLES)]:
      for ci,cell in enumerate(g.CELLS):
       for ti,t in enumerate(tasks):
        rng=random.Random(pseed+100000+ti);lines=[t.request];w=t.init.copy();ctr=0;have_result=False
        for step,oracle in enumerate(t.oracle):
            a,err=plan(lines); exact=int(err is None and a.tup()==oracle.tup());val_exact=int(err is None and a.value==oracle.value);tool_exact=int(err is None and a.tool==oracle.tool);key_exact=int(err is None and a.k1==oracle.k1 and a.k2==oracle.k2)
            rows.append({'panel':pi,'task_id':ti,'kind':t.kind,'ambiguity':ambiguity(t),'schema_regime':regime,'condition':cell.name,'step':step,'after_result':int(have_result),'oracle_tool':oracle.tool,'exact':exact,'tool_exact':tool_exact,'key_exact':key_exact,'value_exact':val_exact,'planner_error':int(err is not None)})
            if oracle.tool=='DONE':break
            ctr=g.append_exec(lines,w,oracle,ctr,rng,cell,pseed+100000+ti+step,styles)
            if oracle.tool in ('READ','READPAIR'):have_result=True
with open(OUT+'/prefix_diagnostics.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# summarize
def mean(q,key):return sum(r[key] for r in q)/len(q) if q else None
summary={}
for reg in ['seen','unseen']:
  summary[reg]={}
  for cell in [c.name for c in g.CELLS]:
    q=[r for r in rows if r['schema_regime']==reg and r['condition']==cell]
    post=[r for r in q if r['after_result']]
    wr=[r for r in post if r['oracle_tool']=='WRITE']
    mw=[r for r in wr if r['ambiguity']=='multi_read']
    summary[reg][cell]={'n':len(q),'overall_exact':mean(q,'exact'),'post_result_exact':mean(post,'exact'),'write_exact':mean(wr,'exact'),'write_value_exact':mean(wr,'value_exact'),'multi_read_write_exact':mean(mw,'exact'),'multi_read_write_value_exact':mean(mw,'value_exact')}
# fixed heldout raw-style semantic planner controls, 600 tasks, P1_N0/P0_N0
def run_sem(t,cell,seed,styles,max_steps=14):
    rng=random.Random(seed);w=t.init.copy();lines=[t.request];ctr=0;oi=0;fd=0;pe=0;vf=0
    for step in range(max_steps):
        a,err=plan(lines)
        if err:pe+=1
        else:
            if not fd and a.tup()!=t.oracle[min(oi,len(t.oracle)-1)].tup():fd=step+1
            oi+=1
            if a.tool in ('READ','READPAIR','WRITE','CLEAR'):ctr=g.append_exec(lines,w,a,ctr,rng,cell,seed+step,styles)
            else:
                if w==t.target:return {'ok':1,'first_div':fd}
                vf+=1
                if vf>=2:break
    return {'ok':int(w==t.target),'first_div':fd}
style_control={}
for st in g.UNSEEN_STYLES:
    style_control[str(st)]={}
    for cell in [g.CELLS[1],g.CELLS[3]]:
        ok=0;n=0;fds=[]
        for pi,pseed in enumerate([SEED_D+50000,SEED_D+60000,SEED_D+70000],1):
            rr=random.Random(pseed);tasks=[g.make_task(rr) for _ in range(200)]
            for ti,t in enumerate(tasks):
                r=run_sem(t,cell,pseed+100000+ti,(st,));ok+=r['ok'];n+=1
                if not r['ok'] and r['first_div']:fds.append(r['first_div'])
        style_control[str(st)][cell.name]={'n':n,'accuracy':ok/n,'mean_first_div_failure':float(np.mean(fds)) if fds else None}
res={'experiment':'TOOL-CHAIN-GEOMETRY-006G diagnostics','prefix':summary,'fixed_unseen_raw_style_control':style_control}
json.dump(res,open(OUT+'/diagnostics.json','w'),indent=2);print(json.dumps(res))
