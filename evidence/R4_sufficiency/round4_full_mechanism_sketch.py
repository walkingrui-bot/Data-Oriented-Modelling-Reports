"""
CE2G-style reproductive continuation geometry
Minimal mechanism sketch used in Round 4.

This is a toy generative mechanism, not an LLM implementation.

Core state
----------
S[a,b] : continuation geometry
M[a]   : inherited local rewrite phenotype
q      : recurrent projection state

One realized transition a -> b
------------------------------
1. Continuation distribution:
       K[a,*] = exp(-S[a,*]/theta)
       P[a,*] = K[a,*] / sum(K[a,*])

2. Event-local rewrite phenotype:
       g = norm(phi[a,b] + gamma * M[a] + mutation/interactions)

3. Descendant rewrite:
       DeltaS_gene[b,k]
           = -eta * centered_similarity(g, phi[b,k])

4. Projection-as-event:
       y = R(g, b, q)
       q <- projection_decay*q + new_projection
       DeltaS_projection = O(y)

5. CE2G-style bounded write:
       alpha = min(1, write_budget / ||DeltaS_proposed||)
       S <- S_ext + geometry_decay*(S-S_ext)
                    + alpha*(DeltaS_gene + DeltaS_projection)

6. Reproductive rewrite inheritance:
       M[b] <- recombine(M[b], g)

Thus the inherited object is not the surface transition.
What persists is part of the way a realized transition rewrites the
continuation geometry available to descendants.
"""
