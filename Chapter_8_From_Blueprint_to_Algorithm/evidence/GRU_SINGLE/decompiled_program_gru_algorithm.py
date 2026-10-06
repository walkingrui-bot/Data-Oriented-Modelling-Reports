# Decompiled operation-order algorithm for the trained single-objective GRU.
# No neural-network weights are used.

P = 13
OPS = [(9,10),(2,7),(4,2),(6,8)]

def answer(facts, x):
    """
    facts: iterable like ["E2O1", "E0O3", "E1O0"], in any presentation order.
    x: integer 0..12
    """
    program = [None, None, None]
    for token in facts:
        edge = int(token[1])
        op = int(token[3])
        program[edge] = op

    value = x
    for op in program:
        a, b = OPS[op]
        value = (a * value + b) % P
    return value
