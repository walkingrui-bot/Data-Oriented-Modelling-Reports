"""Reproduce ASTIG-013D from public SWE-Xplorer mini-SWE-agent trajectories.
Requires internet access. Outputs summary metrics to stdout.
"""
import json,re,urllib.request,math
from collections import Counter
BASE='https://raw.githubusercontent.com/mahirlabibdihan/SWE-Xplorer-Experiments/main/SWE-Bench-Verified/mini-SWE-agent'
MODELS=['qwen-2.5-7b','gpt-5-mini','deepseek-v4-flash']
TASKS=['sympy__sympy-20154','sympy__sympy-24562','sympy__sympy-13757','sympy__sympy-23950','sympy__sympy-24661','sympy__sympy-13551','sympy__sympy-22914','sympy__sympy-19346']
def fetch(m,t):
    with urllib.request.urlopen(f'{BASE}/{m}/main/{t}/{t}.traj.json') as r:return json.load(r)
def command(s):
    m=re.search(r'```bash\s*\n([\s\S]*?)\n```',s or '',re.I);return re.sub(r'\s+',' ',(m.group(1) if m else '').strip().lower())
def prose(s):return re.sub(r'\s+',' ',re.sub(r'```bash[\s\S]*?```',' ',s or '',flags=re.I)).replace('THOUGHT:','').strip().lower()
def retcode(s):
    m=re.search(r'<returncode>(-?\d+)</returncode>',s or '',re.I);return int(m.group(1)) if m else None
def action(c):
    x=' '+re.sub(r'\s+',' ',c.lower())+' '
    if not c:return 'X'
    if 'complete_task_and_submit_final_output' in x or ('git add -a' in x and 'git diff --cached' in x):return 'S'
    if ('apply_patch' in x or 'git apply' in x or 'sed -i' in x or re.search(r'perl\s+[^&;]*\s-i\b',x) or 'write_text(' in x or 'writelines(' in x or re.search(r'open\([^)]*,\s*[\'\"]w',x) or ('.replace(' in x and ('write' in x or 'open(' in x)) or re.search(r'\btee\s+\S+',x) or re.search(r'\b(cat|echo|printf)\b[^;&|]*>\s*[^\s&|]+',x)):return 'E'
    if ('pytest' in x or 'python -m sympy.test' in x or 'python3 -m sympy.test' in x or re.search(r'\btox\b',x) or re.search(r'\bunittest\b',x) or re.search(r'\btest_[a-z0-9_]+',x) or 'assert ' in x or '/tmp/test_' in x or 'test_client()' in x):return 'T'
    y=re.sub(r'^\s*cd /testbed &&\s*','',x).strip()
    if re.match(r'^(ls\b|find\b|grep\b|rg\b|sed -n\b|cat\b|head\b|tail\b|nl\b|pwd\b|awk\b|git status\b|git diff\b|git --no-pager diff\b|git log\b|git show\b)',y):return 'I'
    return 'X'
def states(o,model):
    ms=o.get('messages',[]);out=[]
    for i,m in enumerate(ms):
        if m.get('role')!='assistant':continue
        rc=None
        for z in ms[i+1:i+3]:
            if z.get('role')=='user':rc=retcode(z.get('content',''));break
        c=command(m.get('content',''));out.append({'c':c,'p':prose(m.get('content','')),'a':action(c),'rc':rc,'model':model,'idx':len(out)})
    return out
def recurrence_mass(xs):
    c=Counter(xs);return sum(c[x]>1 for x in xs)/len(xs) if xs else 0
def strong_flags(cs):
    out=[];consec=0
    for i in range(len(cs)):
        w=cs[max(0,i-7):i+1];r=recurrence_mass(w);cand=len(w)>=6 and r>=.5;consec=consec+1 if cand else 0;out.append((len(w)>=6 and r>=.75) or consec>=2)
    return out
def phase(hist):
    edits=[i for i,z in enumerate(hist) if z['a']=='E']
    if not edits:return 'PRE_EDIT'
    since=hist[edits[-1]+1:]
    if not any(z['a'] in {'T','I','X'} for z in since):return 'POST_EDIT_UNVERIFIED'
    tests=[z for z in since if z['a']=='T']
    if tests and tests[-1]['rc'] is not None and tests[-1]['rc']!=0:return 'TEST_FAILED'
    return 'POST_EDIT_VALIDATED'
def primary(p):return {'PRE_EDIT':'E','POST_EDIT_UNVERIFIED':'T','TEST_FAILED':'E','POST_EDIT_VALIDATED':'S'}[p]
def bow(s):
    c=Counter(re.findall(r'[a-z0-9_./:-]+',s));v={k:math.log1p(n) for k,n in c.items()};n=math.sqrt(sum(x*x for x in v.values())) or 1;return v,n
def cosine(a,b):
    va,na=a;vb,nb=b
    if len(va)>len(vb):va,vb=vb,va
    return sum(x*vb.get(k,0) for k,x in va.items())/(na*nb)
D={(m,t):states(fetch(m,t),m) for m in MODELS for t in TASKS}
for k in D:
    for z in D[k]:z['v']=bow(z['p'])
summary={'n':0,'blind_ok':0,'blind_prem_s':0,'blind_roles':Counter(),'phase_roles':Counter(),'milestone3':0,'clean5':0,'submit5':0,'minH':Counter(),'successH':Counter(),'terminalH':Counter(),'clearH':Counter()}
for t in TASKS:
    q=D[('qwen-2.5-7b',t)];orig=[z['c'] for z in q];flags=strong_flags(orig);ext=D[('gpt-5-mini',t)]+D[('deepseek-v4-flash',t)]
    for i in range(len(q)):
        if not(i and flags[i-1]):continue
        summary['n']+=1;p=phase(q[:i]);pr=primary(p);seen={z['c'] for z in q[:i]};qv=q[i]['v']
        prog=sorted(({**z,'sim':cosine(qv,z['v'])} for z in ext if z['c'] and z['c'] not in seen and z['a'] in 'ETS'),key=lambda z:z['sim'],reverse=True)
        blind=prog[0];pa=next(z for z in prog if z['a']==pr);summary['blind_roles'][blind['a']]+=1;summary['phase_roles'][pa['a']]+=1
        summary['blind_ok']+=blind['a']==pr;summary['blind_prem_s']+=blind['a']=='S' and p!='POST_EDIT_VALIDATED'
        src=D[(pa['model'],t)]
        # milestone within 3
        roll=src[pa['idx']:pa['idx']+3];mil=False
        if p=='POST_EDIT_VALIDATED':mil=pa['a']=='S'
        elif p=='PRE_EDIT':mil=pa['a']=='E' and any(z['a'] in {'I','T','X'} for z in roll[1:])
        elif p=='POST_EDIT_UNVERIFIED':mil=pa['a']=='T' and (pa['rc']==0 or any(z['a']=='E' for z in roll[1:]))
        summary['milestone3']+=mil
        r5=src[pa['idx']:pa['idx']+5];summary['clean5']+=all(z['c'] not in {h['c'] for h in q[max(0,i-4):i]} for z in r5);summary['submit5']+=any(z['a']=='S' for z in r5)
        first=None
        for H in range(1,6):
            raw=src[pa['idx']:pa['idx']+H];si=next((j for j,z in enumerate(raw) if z['a']=='S'),-1);seg=raw[:si+1] if si>=0 else raw;terminal=si>=0;clear=False
            if not terminal and len(seg)==H:
                cf=orig[:i]+[z['c'] for z in seg]+orig[i+len(seg):];ff=strong_flags(cf);clear=not ff[i+len(seg)-1]
            if terminal:summary['terminalH'][H]+=1
            if clear:summary['clearH'][H]+=1
            if terminal or clear:
                summary['successH'][H]+=1
                if first is None:first=H
        summary['minH'][first if first else '>5']+=1
print(json.dumps(summary,default=dict,indent=2))
