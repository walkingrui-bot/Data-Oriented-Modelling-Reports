import sys,torch,numpy as np,json
sys.path.insert(0,'/mnt/data'); import importlib,internal_coord_003_multilang_fast as m; importlib.reload(m)
CMPSETS={'>':{'greater_than','大于','より大きい','mayor_que','>'},'<':{'less_than','小于','より小さい','menor_que','<'}}
RET={'en':'return','zh':'返回','ja':'返す','es':'devuelve','py':'return','js':'return'}

def parse_expr(toks,pos):
    # pos points at first coeff token
    try:
        a=int(toks[pos]); assert toks[pos+1]=='*' and toks[pos+2]=='x'; j=pos+3; b=0
        if j+1<len(toks) and toks[j] in ['+','-']:
            b=int(toks[j+1])*(1 if toks[j]=='+' else -1)
        return a,b
    except Exception: return None

def parse(toks,lang):
    try:
        cmp_tok=None; ci=None
        for i,t in enumerate(toks):
            if any(t in s for s in CMPSETS.values()): cmp_tok=t;ci=i;break
        if cmp_tok is None:return None
        cmp_='>' if cmp_tok in CMPSETS['>'] else '<'
        t=int(toks[ci-1] if lang=='ja' else toks[ci+1])
        r=RET[lang]; inds=[i for i,x in enumerate(toks) if x==r]
        if len(inds)<2:return None
        e1=parse_expr(toks,inds[0]+1);e2=parse_expr(toks,inds[1]+1)
        if e1 is None or e2 is None:return None
        return (cmp_,t,e1[0],e1[1],e2[0],e2[1])
    except Exception:return None

def f(scene,x):
    c,t,a,b,d,e=scene;return a*x+b if (x>t if c=='>' else x<t) else d*x+e

def audit(model,scenes,n=40):
    ok=[]; parseok=[]; exact=[]; details=[]; xs=[-5,-2,0,2,5]
    for s in scenes[:n]:
        for si,slang in enumerate(m.LANGS):
            x,le=m.pad([m.encode(s,slang)],m.DEVICE); z=model.encode(x,le,torch.tensor([si],device=m.DEVICE))
            for ti,tlang in enumerate(m.LANGS):
                if ti==si: continue
                ids=model.gen(z,torch.tensor([ti],device=m.DEVICE),maxlen=40)[0]; toks=[m.ITOS[k] for k in ids]
                ps=parse(toks,tlang); parseok.append(ps is not None); exact.append(ids==m.encode(s,tlang)[:-1])
                good=ps is not None and all(f(ps,xv)==f(s,xv) for xv in xs);ok.append(good)
                if len(details)<8:details.append({'scene':s,'src':slang,'tgt':tlang,'generated':' '.join(toks),'parsed':ps,'semantic_exec':good})
    return {'cross_exact':float(np.mean(exact)),'parse_rate':float(np.mean(parseok)),'execution_equivalence':float(np.mean(ok)),'details':details}

if __name__=='__main__':
 paths={
 's0_self':'/mnt/data/IC003v2_self600.pt','s0_bind':'/mnt/data/IC003v2_bind650.pt','s0_shuffle':'/mnt/data/IC003v2_shuffle650.pt',
 's2_self':'/mnt/data/IC003_s2_self.pt','s2_bind':'/mnt/data/IC003_s2_bind.pt','s2_shuffle':'/mnt/data/IC003_s2_shuffle.pt',
 's3_self':'/mnt/data/IC003_s3_self.pt','s3_bind':'/mnt/data/IC003_s3_bind.pt','s3_shuffle':'/mnt/data/IC003_s3_shuffle.pt'}
 out={}
 for name,p in paths.items():
  model=m.M().to(m.DEVICE);model.load_state_dict(torch.load(p,map_location='cpu')); model.eval(); r=audit(model,m.ALL_SCENES[1000:1200],n=30);out[name]=r;print(name,{k:r[k] for k in ['cross_exact','parse_rate','execution_equivalence']})
 json.dump(out,open('/mnt/data/IC003_execution_audit.json','w'),ensure_ascii=False,indent=2)
