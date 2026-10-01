"""Reproduce ASTIG-013C phase-state and role-availability metrics.

Requires internet access to public GitHub raw trajectory files.
Run from a directory that also contains astig013b_task_results_prior.csv.
"""
import json, re, urllib.request, csv
from collections import Counter

BASE='https://raw.githubusercontent.com/mahirlabibdihan/SWE-Xplorer-Experiments/main/SWE-Bench-Verified/mini-SWE-agent'
MODELS=['gpt-5-mini','deepseek-v4-flash','qwen-2.5-7b']
TASKS=['sympy__sympy-16886','pallets__flask-5014','sympy__sympy-20154','sympy__sympy-24562','sympy__sympy-13757','sympy__sympy-23950','sympy__sympy-24661','sympy__sympy-13551','sympy__sympy-22914','sympy__sympy-19346']
LOOP_TASKS=['sympy__sympy-20154','sympy__sympy-24562','sympy__sympy-13757','sympy__sympy-23950','sympy__sympy-24661','sympy__sympy-13551','sympy__sympy-22914','sympy__sympy-19346']

def fetch(model,task):
    u=f'{BASE}/{model}/main/{task}/{task}.traj.json'
    with urllib.request.urlopen(u) as r:
        return json.load(r)

def command(s):
    m=re.search(r'```bash\s*\n([\s\S]*?)\n```',s or '',re.I)
    return re.sub(r'\s+',' ',(m.group(1) if m else '').strip().lower())

def retcode(s):
    m=re.search(r'<returncode>(-?\d+)</returncode>',s or '',re.I)
    return int(m.group(1)) if m else None

def action(c):
    x=' '+re.sub(r'\s+',' ',c.lower())+' '
    if not c: return 'X'
    if 'complete_task_and_submit_final_output' in x or ('git add -a' in x and 'git diff --cached' in x): return 'S'
    edit=(
        'apply_patch' in x or 'git apply' in x or 'sed -i' in x or re.search(r'perl\s+[^&;]*\s-i\b',x)
        or 'write_text(' in x or 'writelines(' in x or re.search(r'open\([^)]*,\s*[\'\"]w',x)
        or ('.replace(' in x and ('write' in x or 'open(' in x)) or re.search(r'\btee\s+\S+',x)
        or re.search(r'\b(cat|echo|printf)\b[^;&|]*>\s*[^\s&|]+',x)
    )
    if edit: return 'E'
    test=(
        'pytest' in x or 'python -m sympy.test' in x or 'python3 -m sympy.test' in x
        or re.search(r'\btox\b',x) or re.search(r'\bunittest\b',x) or re.search(r'\btest_[a-z0-9_]+',x)
        or 'assert ' in x or '/tmp/test_' in x or 'test_client()' in x
    )
    if test: return 'T'
    y=re.sub(r'^\s*cd /testbed &&\s*','',x).strip()
    if re.match(r'^(ls\b|find\b|grep\b|rg\b|sed -n\b|cat\b|head\b|tail\b|nl\b|pwd\b|awk\b|git status\b|git diff\b|git --no-pager diff\b|git log\b|git show\b)',y): return 'I'
    return 'X'

def states(o):
    ms=o.get('messages',[]); out=[]
    for i,m in enumerate(ms):
        if m.get('role')!='assistant': continue
        rc=None
        for z in ms[i+1:i+3]:
            if z.get('role')=='user':
                rc=retcode(z.get('content','')); break
        c=command(m.get('content',''))
        out.append({'c':c,'a':action(c),'rc':rc})
    return out

def recurrence_mass(xs):
    c=Counter(xs)
    return sum(c[x]>1 for x in xs)/len(xs) if xs else 0.0

def strong_flags(cmds):
    out=[]; consec=0
    for i in range(len(cmds)):
        w=cmds[max(0,i-7):i+1]; r=recurrence_mass(w)
        cand=len(w)>=6 and r>=0.50
        consec=consec+1 if cand else 0
        out.append((len(w)>=6 and r>=0.75) or consec>=2)
    return out

def phase(hist):
    edits=[i for i,z in enumerate(hist) if z['a']=='E']
    if not edits: return 'PRE_EDIT'
    e=edits[-1]; since=hist[e+1:]
    if not any(z['a'] in {'T','I','X'} for z in since): return 'POST_EDIT_UNVERIFIED'
    tests=[z for z in since if z['a']=='T']
    if tests and tests[-1]['rc'] is not None and tests[-1]['rc']!=0: return 'TEST_FAILED'
    return 'POST_EDIT_VALIDATED'

def primary_role(p):
    return {'PRE_EDIT':'E','POST_EDIT_UNVERIFIED':'T','TEST_FAILED':'E','POST_EDIT_VALIDATED':'S'}[p]

# Cache all 30 trajectories
D={(m,t):states(fetch(m,t)) for m in MODELS for t in TASKS}

# Submitted calibration
cal=[]
for m in ['gpt-5-mini','deepseek-v4-flash']:
    for t in TASKS:
        st=D[(m,t)]
        for i,z in enumerate(st):
            if z['a']=='S':
                hist=st[:i]; edits=[j for j,h in enumerate(hist) if h['a']=='E']; e=edits[-1] if edits else None
                since=[] if e is None else hist[e+1:]
                cal.append({
                    'model':m,'task':t,'steps':len(st),'submit_phase_strict':phase(hist),
                    'has_edit_before_submit':int(e is not None),
                    'post_edit_validation_before_submit':int(any(h['a'] in {'T','I','X'} for h in since)),
                    'post_edit_test_before_submit':int(any(h['a']=='T' for h in since)),
                })
with open('astig013c_successful_phase_calibration.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=cal[0].keys()); w.writeheader(); w.writerows(cal)

# Qwen strong-loop phases and external role availability
phase_rows=[]; avail_rows=[]
for t in LOOP_TASKS:
    q=D[('qwen-2.5-7b',t)]; flags=strong_flags([z['c'] for z in q])
    ext=D[('gpt-5-mini',t)]+D[('deepseek-v4-flash',t)]
    pc=Counter(); ac=Counter(); strong=0
    for i in range(len(q)):
        if not (i and flags[i-1]): continue
        strong+=1; p=phase(q[:i]); pc[p]+=1
        seen={z['c'] for z in q[:i]}
        roles={z['a'] for z in ext if z['c'] and z['c'] not in seen}
        for a in 'ETS': ac[a]+=int(a in roles)
        ac['P']+=int(primary_role(p) in roles)
    phase_rows.append({'task':t,'strong_states':strong,'pre_edit':pc['PRE_EDIT'],'post_edit_unverified':pc['POST_EDIT_UNVERIFIED'],'post_edit_validated':pc['POST_EDIT_VALIDATED'],'test_failed':pc['TEST_FAILED']})
    avail_rows.append({'task':t,'strong_states':strong,'edit_available':ac['E'],'test_available':ac['T'],'submit_available':ac['S'],'phase_primary_role_available':ac['P']})
for name,rows in [('astig013c_qwen_phase_counts.csv',phase_rows),('astig013c_candidate_role_availability.csv',avail_rows)]:
    with open(name,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

print('Submitted calibration:',len(cal),'trajectories')
print('Final submits with edit + post-edit validation:',sum(x['has_edit_before_submit'] and x['post_edit_validation_before_submit'] for x in cal),'/',len(cal))
print('Qwen strong states:',sum(x['strong_states'] for x in phase_rows))
print('Phase totals:',{k:sum(x[k] for x in phase_rows) for k in ['pre_edit','post_edit_unverified','post_edit_validated','test_failed']})
print('Primary-role availability:',sum(x['phase_primary_role_available'] for x in avail_rows),'/',sum(x['strong_states'] for x in avail_rows))
