from strips.hsp import compute_costs
from misc.functions import argmin, flatten, INF

def get_layers(costs):
    num_layers = max(pair.level for pair in costs.values()) + 1
    layers = [[] for _ in range(num_layers)]
    for value, (_, level) in costs.items():
        layers[level].append(value)
    return layers

# def print_rpg(literal_layers, operator_layers):
#     for level in range(len(literal_layers)):
#         print('Level', level)
#         if level != 0:
#             print('Operators', str_iterable(operator_layers[level-1]))
#         print('Literals', str_iterable(literal_layers[level]), '\n')

def extract_relaxed_plan(goal, literal_costs, operator_costs):
    #literal_layers = get_layers(literal_costs)
    operator_layers = get_layers(operator_costs)
    #print_rpg(literal_layers, operator_layers)
    num_goal_layers = operator_costs[goal].level + 1
    goals = [set() for _ in range(num_goal_layers)]
    plan = [set() for _ in range(num_goal_layers - 1)]
    marked = [set() for _ in range(num_goal_layers)]

    for literal in goal.conditions:
        goals[literal_costs[literal].level].add(literal)

    for level in reversed(range(1, num_goal_layers)):
        for literal in goals[level]:
            if literal in marked[level]:
                continue
            easiest_operator = argmin(lambda o: operator_costs[o].cost,
                    (o for o in operator_layers[level-1] if literal in o.effects))
            #easiest_operator = argmin(lambda o: operator_costs[o].cost,
            #        (o for o, p in operator_costs.items() if p.level < level and literal in o.effects))
            plan[level-1].add(easiest_operator)
            for condition in easiest_operator.conditions:
                goals[literal_costs[condition].level].add(condition)
            for effect in easiest_operator.effects:
                marked[level].add(effect)
                marked[level-1].add(effect)
    return plan, goals

###########################################################################

def plan_cost(relaxed_plan, unit=False):
    if relaxed_plan is None:
        return INF
    return sum(operator.cost if not unit else 1
               for operator in flatten(relaxed_plan))

def plan_length(relaxed_plan):
    if relaxed_plan is None:
        return INF
    return len(flatten(relaxed_plan))

def multi_cost(goal, operator_costs, relaxed_plan, relaxed_goals):
    return plan_cost(relaxed_plan), operator_costs[goal].cost, operator_costs[goal].level

###########################################################################

# TODO: use FF or FD software for heuristics

def none(operator_costs, relaxed_plan, relaxed_goals):
    return []

def applicable(operator_costs, relaxed_plan, relaxed_goals):
    return [o for o, (_, level) in operator_costs.items() if level == 0]

def backpointers(operator_costs, relaxed_plan, relaxed_goals):
    # Retrace actions without using extract_relaxed_plan
    # Could also do h_max and h_add versions
    raise NotImplementedError()

def first_goals(operator_costs, relaxed_plan, relaxed_goals):
    if len(relaxed_goals) <= 1:
        return []
    return [o for o, (_, level) in operator_costs.items()
            if (level == 0) and any(effect in relaxed_goals[1] for effect in o.effects)]

def first_operators(operator_costs, relaxed_plan, relaxed_goals):
    if not relaxed_plan:
        return []
    return relaxed_plan[0]

# TODO: prioritize helpful actions

###########################################################################

def ff(state, goal, operators, heuristic, helpful_actions, op=max, unit=False):
    literal_costs, operator_costs = compute_costs(state, goal, operators, op=op, unit=unit)
    if goal not in operator_costs:
        return INF, []
    relaxed_plan, relaxed_goals = extract_relaxed_plan(goal, literal_costs, operator_costs)
    return heuristic(relaxed_plan), helpful_actions(operator_costs, relaxed_plan, relaxed_goals)

def ff_fn(heuristic, helpful_actions, op=max, unit=False):
    return lambda s, g, o: ff(s, g, o, heuristic, helpful_actions, op=op, unit=unit)

###########################################################################

def h_ff_max(*args):
    return ff_fn(plan_cost, none, op=max)(*args)[0]

def h_ff_add(*args):
    return ff_fn(plan_cost, none, op=sum)(*args)[0]
