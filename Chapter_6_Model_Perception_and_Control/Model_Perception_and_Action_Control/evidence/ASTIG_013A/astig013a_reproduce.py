"""Reproduce ASTIG-013A cooldown edge-interception metrics from public mini-SWE-agent trajectories."""
import json, re, urllib.request, csv
from collections import Counter
BASE='https://raw.githubusercontent.com/mahirlabibdihan/SWE-Xplorer-Experiments/main/SWE-Bench-Verified/mini-SWE-agent'
MODELS=['gpt-5-mini','deepseek-v4-flash','qwen-2.5-7b']
TASKS=['sympy__sympy-16886','pallets__flask-5014','sympy__sympy-20154','sympy__sympy-24562','sympy__sympy-13757','sympy__sympy-23950','sympy__sympy-24661','sympy__sympy-13551','sympy__sympy-22914','sympy__sympy-19346']

def fetch(model,task):
    u=f'{BASE}/{model}/main/{task}/{task}.traj.json'
    with urllib.request.urlopen(u) as r: return json.load(r)

def command(content):
    m=re.search(r'```bash\s*\n([\s\S]*?)\n```',content or '',re.I)
    s=(m.group(1) if m else '').strip().lower()
    return re.sub(r'\s+',' ',s)

def recurrence_mass(xs):
    if not xs: return 0.0
    c=Counter(xs)
    return sum(c[x]>1 for x in xs)/len(xs)

def strong_flags(cmds):
    out=[]; consec=0
    for i in range(len(cmds)):
        w=cmds[max(0,i-7):i+1]; r=recurrence_mass(w)
        cand=len(w)>=6 and r>=.50
        consec=consec+1 if cand else 0
        out.append((len(w)>=6 and r>=.75) or consec>=2)
    return out

def gap(cmds,t):
    for j in range(t-1,-1,-1):
        if cmds[j]==cmds[t]: return t-j
    return None

rows=[]
for model in MODELS:
    for task in TASKS:
        o=fetch(model,task)
        cmds=[command(m.get('content','')) for m in o.get('messages',[]) if m.get('role')=='assistant']
        flags=strong_flags(cmds)
        status=o.get('info',{}).get('exit_status')
        for t,c in enumerate(cmds):
            ps=flags[t-1] if t else False
            g=gap(cmds,t)
            rec={'model':model,'task':task,'status':status,'step':t+1,'prior_strong':int(ps),'repeat_gap':g or ''}
            for h in [1,2,4,8]: rec[f'blocked_h{h}']=int(g is not None and g<=h); rec[f'gated_h{h}']=int(ps and g is not None and g<=h)
            rows.append(rec)
with open('astig013a_state_edges.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print('wrote',len(rows),'state-edge records')
