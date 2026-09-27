import runpy, re, json, numpy as np
from collections import Counter, defaultdict
ns=runpy.run_path('/mnt/data/code_geometry_005a.py')
ROOT=ns['ROOT']; parsers=ns['parsers']; exts=ns['exts']; corpora=ns['corpora']; tree_metrics=ns['tree_metrics']

CATS=['FUNC','PARAM','TYPE','BLOCK','DECL','ASSIGN','BRANCH','LOOP','RETURN','CALL','INDEX','OP','ID','LITERAL','ATTR','COLLECTION']

def canon(lang, t):
    s=t.lower()
    # precise skips first
    if s in {'load','store','del','modifier','modifiers','expression_statement','firststatement','array','args_add_block','var_ref','var_field','argument','argument_list','inout_expr','has_initial_value_attr','has_storage_attr','conditions=array','pattern_entry','fieldlist','file','compilation_unit','module','sourcefile'}:
        return None
    # function / method declarations
    if any(k in s for k in ['functiondef','functiondeclaration','functiondecl','funcdecl','func_decl']) or s in {'method','def'}:
        return 'FUNC'
    # params
    if s in {'arg','parameter','parmvard ecl'.replace(' ',''),'parmvar_decl','parmvarddecl','params','field'} or 'parameter' in s or 'parmvar' in s:
        return 'PARAM'
    # type forms. Do this before collection because ArrayType is a type.
    if 'type' in s or s in {'numberkeyword','stringkeyword','booleankeyword'}:
        return 'TYPE'
    # blocks / bodies
    if s in {'block','compoundstmt','blockstmt','brace_stmt','bodystmt','brace_block'} or s.endswith('block'):
        return 'BLOCK'
    # branching
    if s.startswith('if') or s=='conditional_expression' or s=='conditionalexpression':
        return 'BRANCH'
    # loops
    if any(k in s for k in ['whilestmt','while_loop','while','forstmt','for_loop','forofstatement','forinstatement','rangestmt','range_stmt']) or s.startswith('for'):
        return 'LOOP'
    # return
    if 'return' in s:
        return 'RETURN'
    # assignment before declarations
    if any(k in s for k in ['augassign','assignstmt','assignment','firstassignment','compoundassign','opassign','massign']) or s=='assign':
        return 'ASSIGN'
    # declarations
    if any(k in s for k in ['vardecl','var_decl','variabledeclaration','declaration','pattern_binding_decl','patternbindingdecl']) or s=='variable':
        return 'DECL'
    # calls
    if any(k in s for k in ['callexpr','call_expr','callexpression','method_invocation','methodinvocation','dot_syntax_call_expr','method_add_block']) or s=='call':
        return 'CALL'
    # indexing/subscript
    if any(k in s for k in ['subscript','elementaccess','array_access','arrayaccess','indexexpr','aref']):
        return 'INDEX'
    # member/attribute access
    if any(k in s for k in ['attribute','propertyaccess','member_select','memberselect']):
        return 'ATTR'
    # collections
    if any(k in s for k in ['tuple','list','arrayliteral','array_literal']) or s in {'array_type'}:
        return 'COLLECTION'
    # literals before ID
    if 'literal' in s or s in {'constant','basiclit','firstliteraltoken','@int','@float','@tstring_content','cxxboolliteralexpr','characterliteral','integerliteral','int_literal','char_literal'}:
        return 'LITERAL'
    # identifiers / refs
    if s in {'name','identifier','declrefexpr','ident','declref_expr','@ident','pattern_named'}:
        return 'ID'
    # operators: broad catch after declaration/call etc
    if any(k in s for k in ['binop','binary','operator','compare','unary','postfix','prefix','less_than','greater_than','equal_to','not_equal','plus','minus','multiply','divide','remainder','conditional_and','conditional_or']):
        return 'OP'
    return None

def canonicalize(lang,nodes,edges):
    ch=defaultdict(list); indeg=[0]*len(nodes)
    for a,b in edges: ch[a].append(b); indeg[b]+=1
    roots=[i for i,d in enumerate(indeg) if d==0]
    cn=[]; ce=[]
    def rec(i,parent_c=None):
        lab=canon(lang,nodes[i])
        if lab is not None:
            me=len(cn); cn.append(lab)
            if parent_c is not None: ce.append((parent_c,me))
            p=me
        else: p=parent_c
        for j in ch.get(i,[]): rec(j,p)
    for r in roots: rec(r,None)
    return cn,ce

rows=[]
for lang in corpora:
    nodes,edges=parsers[lang](ROOT/f"bench.{exts[lang]}")
    cn,ce=canonicalize(lang,nodes,edges)
    tm=tree_metrics(cn,ce)
    cnt=Counter(cn); total=sum(cnt.values())
    row={'language':lang,'canonical_nodes':total,**tm,'cat_counts':dict(cnt)}
    rows.append(row)

print('language\tcanon_nodes\tcanon_sr\tcanon_top3\tmax_depth\tmean_branch\ttype_entropy')
for r in rows:
    print(f"{r['language']}\t{r['canonical_nodes']}\t{r['ast_stable_rank']:.3f}\t{r['ast_top3']:.3f}\t{r['max_depth']}\t{r['mean_branch']:.3f}\t{r['type_entropy']:.3f}")

print('\nCategory shares:')
print('lang\t'+'\t'.join(CATS))
for r in rows:
    tot=r['canonical_nodes']; cnt=r['cat_counts']
    print(r['language']+'\t'+'\t'.join(f"{cnt.get(c,0)/tot:.3f}" for c in CATS))

# Jensen-Shannon distances on canonical category distributions
P=np.array([[r['cat_counts'].get(c,0)+1e-6 for c in CATS] for r in rows],float); P=P/P.sum(1,keepdims=True)
def js(p,q):
    m=(p+q)/2
    kl=lambda a,b: np.sum(a*np.log2(a/b))
    return np.sqrt(0.5*kl(p,m)+0.5*kl(q,m))
D=np.array([[js(P[i],P[j]) for j in range(len(rows))] for i in range(len(rows))])
langs=[r['language'] for r in rows]
print('\nNearest by canonical category JS distance:')
for i,l in enumerate(langs):
    idx=np.argsort(D[i])[1:4]
    print(l,[(langs[j],round(float(D[i,j]),3)) for j in idx])

out={'categories':CATS,'rows':rows,'js_distance':{'languages':langs,'values':D.tolist()}}
(ROOT/'canonical_results.json').write_text(json.dumps(out,indent=2))
