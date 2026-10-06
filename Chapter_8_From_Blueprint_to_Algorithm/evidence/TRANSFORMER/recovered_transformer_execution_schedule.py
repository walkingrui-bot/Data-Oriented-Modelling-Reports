# Recovered execution schedule from the controlled causal-Transformer experiment.
# This is the explicit program implemented by the forward trace behavior.

P = 13
OPS = [(9,10),(2,7),(4,2),(6,8)]

def apply_op(op, value):
    a, b = OPS[op]
    return (a * value + b) % P

def execute_forward_cot(facts, initial_value):
    """
    facts: mapping {0: op_for_E0, 1: op_for_E1, 2: op_for_E2}
    Returns the operation/value trace and final answer.
    """
    state = initial_value
    trace = []
    for slot in (0, 1, 2):
        op = facts[slot]                 # retrieve scheduled operator
        state = apply_op(op, state)      # local transformation
        trace.append((slot, op, state))  # externalize new computational state
    return trace, state
