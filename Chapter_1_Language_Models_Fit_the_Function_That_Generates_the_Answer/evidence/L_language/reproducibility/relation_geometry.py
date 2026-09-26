"""Minimal recurrence/bridge metrics used in the archive.
Input: token sequence (already normalized/tokenized).
This is a reference implementation for the descriptive genre/translator analyses,
not a claim that this exact metric is the final neural mechanism.
"""
from collections import Counter
import math

def _mean(xs):
    return sum(xs)/len(xs) if xs else 0.0

def _sd(xs):
    if len(xs) < 2: return 0.0
    m=_mean(xs)
    return math.sqrt(sum((x-m)**2 for x in xs)/(len(xs)-1))

def relation_geometry(tokens, bridge_radius=4):
    N=len(tokens)
    last={}; gaps=[]; arcs=[]; repeated_positions=[]
    for i,t in enumerate(tokens):
        if t in last:
            gaps.append(i-last[t]); arcs.append((last[t],i,t)); repeated_positions.append(i)
        last[t]=i
    rec=len(gaps)/N if N else 0.0
    local=sum(d<=8 for d in gaps)/len(gaps) if gaps else 0.0
    mid=sum(8<d<=24 for d in gaps)/len(gaps) if gaps else 0.0
    long=sum(d>24 for d in gaps)/len(gaps) if gaps else 0.0
    mg=_mean(gaps); gap_cv=_sd(gaps)/mg if mg else 0.0
    bridges=[]
    for p,i,t in arcs:
        A=set(tokens[max(0,p-bridge_radius):p] + tokens[p+1:min(N,p+bridge_radius+1)])
        B=set(tokens[max(0,i-bridge_radius):i] + tokens[i+1:min(N,i+bridge_radius+1)])
        A.discard(t); B.discard(t)
        union=len(A|B)
        if union: bridges.append(len(A&B)/union)
    def repeated_ngram(n):
        seq=[tuple(tokens[i:i+n]) for i in range(max(0,N-n+1))]
        c=Counter(seq)
        return sum(v-1 for v in c.values() if v>1)/max(1,len(seq))
    bins=[0]*8
    for i in repeated_positions:
        bins[min(7,int(8*i/N))]+=1
    bm=_mean(bins)
    burst_cv=(math.sqrt(_mean([(x-bm)**2 for x in bins]))/bm) if bm else 0.0
    return dict(rec=rec,local=local,mid=mid,long=long,gap_cv=gap_cv,
                bridge=_mean(bridges),bigram=repeated_ngram(2),
                trigram=repeated_ngram(3),burst_cv=burst_cv)
