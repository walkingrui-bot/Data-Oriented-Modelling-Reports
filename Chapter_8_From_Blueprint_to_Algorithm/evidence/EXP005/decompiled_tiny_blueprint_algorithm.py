# Decompiled from TINY BLUEPRINT EXP003B/005
# Valid domain:
# - three goal->operation facts form a permutation of operations {0,1,2}
# - goal in {0,1,2}
# - order_bit/style_bit in {0,1}
# - x,y in 0..10
#
# This program was inferred from the trained network's parameterized behavior.
# It contains no neural-network weights.

COEFF = {
    (0,0):(1,2),
    (0,1):(2,1),
    (1,0):(2,3),
    (1,1):(3,2),
    (2,0):(4,1),
    (2,1):(1,4),
}

def answer(facts, goal, order_bit, style_bit, x, y):
    # The trained planner causally ignores the queried fact and uses the other two.
    other_ops = [op for fact_goal, op in facts if fact_goal != goal]
    missing = list({0,1,2} - set(other_ops))
    if len(missing) != 1:
        raise ValueError("Expected a valid permutation context.")
    operation = missing[0]

    a, b = COEFF[(operation, order_bit)]
    value = (a*x + b*y) % 11

    style = style_bit ^ int(goal == 2)
    return (f"V{value}", "DOT") if style == 0 else ("BOX", f"V{value}")

if __name__ == "__main__":
    demo = [(0,2),(1,0),(2,1)]
    print(answer(demo, goal=1, order_bit=0, style_bit=1, x=3, y=7))
