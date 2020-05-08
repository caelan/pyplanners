from hsp import *
from operators import Axiom

# TODO - Recursively linearize goals to take advantage of multiple effects
# TODO - Use Steiner Tree heuristic/approximation algorithm

def get_layers(costs):
  num_layers = max(pair.level for pair in costs.values()) + 1
  layers = [[] for _ in range(num_layers)]
  for value, (_, level) in costs.items():
    layers[level].append(value)
  return layers

###########################################################################

def flat_layer(_, layer):
  return [(var, value) for var in layer for value in layer[var]]

def random_layer(_, layer):
  return randomize(flat_layer(_, layer))

def easy_layer(costs, layer):
  return sorted(flat_layer(costs, layer), key=lambda item: costs[item[0]][item[1]])

def hard_layer(costs, layer):
  return reversed(easy_layer(costs, layer))

###########################################################################

def zero_cost(*args): return 0
def operator_cost(operator, operator_costs, **args): return operator_costs[operator]
def new_conditions_cost(operator, operator_costs, variable_costs, goals): # TODO - include marked pruning
  nodes = [variable_costs[var][value] for var, value in operator.cond()
           if value not in goals[variable_costs[var][value].level][var]]
  return Node(safe_function(sum, [n.cost for n in nodes], 0), # TODO - should be consistent with op
                  safe_function(max, [n.cost for n in nodes], 0))

ALL_BACK_POINTERS = False
LAYER_ORDER = easy_layer
EASIEST_HEURISTIC = new_conditions_cost

def extract_relaxed_plan(goal, variable_costs, operator_costs):
  operator_layers = get_layers(operator_costs)
  num_goal_layers = operator_costs[goal].level + 1
  goals = [{var: set() for var in variable_costs.keys()} for _ in range(num_goal_layers)]
  plan = [set() for _ in range(num_goal_layers - 1)]
  marked = [{var: set() for var in variable_costs.keys()} for _ in range(num_goal_layers)]

  for var, value in goal.conditions.items():
    goals[variable_costs[var][value].level][var].add(value)

  for level in reversed(range(1, num_goal_layers)):
    for var, value in LAYER_ORDER(variable_costs, goals[level]):
      if value in marked[level][var]: continue
      if ALL_BACK_POINTERS:
        easiest_operator = argmin(lambda o: EASIEST_HEURISTIC(o, operator_costs, variable_costs, goals),
          (o for o, n in operator_costs.items() if n.level < level and var in o.effects and o.effects[var] == value))
      else:
        easiest_operator = argmin(lambda o: EASIEST_HEURISTIC(o, operator_costs, variable_costs, goals),
          (o for o in operator_layers[level-1] if var in o.effects and o.effects[var] == value))
      plan[level-1].add(easiest_operator)
      for var2, value2 in easiest_operator.conditions.items():
        if value2 not in marked[level-1][var2]:
          goals[variable_costs[var2][value2].level][var2].add(value2)
      for var2, value2 in easiest_operator.effects.items():
        marked[level][var2].add(value2)
        marked[level-1][var2].add(value2) # Assumes that actions are read off in order they are selected (no need to reachieve)
  return plan, goals

###########################################################################

def plan_cost(goal, operator_costs, relaxed_plan, relaxed_goals):
  return sum(operator.cost for operator in flatten(relaxed_plan))

def plan_length(goal, operator_costs, relaxed_plan, relaxed_goals):
  return len(flatten(relaxed_plan))

def multi_cost(goal, operator_costs, relaxed_plan, relaxed_goals):
  return plan_cost(goal, operator_costs, relaxed_plan, relaxed_goals), operator_costs[goal].cost, operator_costs[goal].level

###########################################################################

def filter_axioms(operators):
  return list(filter(lambda o: not isinstance(o, Axiom), operators))

def none(goal, operator_costs, relaxed_plan, relaxed_goals):
  return []

def applicable(goal, operator_costs, relaxed_plan, relaxed_goals):
  return filter_axioms([o for o, (_, level) in operator_costs.items() if level == 0])

def first_goals(goal, operator_costs, relaxed_plan, relaxed_goals):
  if len(relaxed_plan) == 0:
      return [] # TODO - weird bug where the current state is the goal so the relaxed plan is empty...probably relates to costs
  return filter_axioms([o for o, (_, level) in operator_costs.items() if level == 0 and any(value in relaxed_goals[1][var] for var, value in o.effects.items())])

def first_operators(goal, operator_costs, relaxed_plan, relaxed_goals):
  if len(relaxed_plan) == 0:
      return []
  return filter_axioms(list(relaxed_plan[0]))

def first_combine(goal, operator_costs, relaxed_plan, relaxed_goals):
  one = first_operators(goal, operator_costs, relaxed_plan, relaxed_goals)
  two = first_goals(goal, operator_costs, relaxed_plan, relaxed_goals) # TODO - include applicable
  return filter_axioms(list(one) + list(set(two) - set(one)))

###########################################################################

def ff(state, goal, operators, heuristic, helpful_actions, op=sum, unit=False):
  variable_costs, operator_costs = compute_costs(state, goal, operators, op=op, unit=unit)
  if goal not in operator_costs: return None, []
  relaxed_plan, relaxed_goals = extract_relaxed_plan(goal, variable_costs, operator_costs)
  return heuristic(goal, operator_costs, relaxed_plan, relaxed_goals), helpful_actions(goal, operator_costs, relaxed_plan, relaxed_goals)

def ff_fn(heuristic, helpful_actions, op=sum, unit=False):
  return lambda s, g, o: ff(s, g, o, heuristic, helpful_actions, op=op, unit=unit)

###########################################################################

def h_ff_max(state, goal, operators):
  return ff(state, goal, operators, plan_cost, none, op=max)[0]

def h_ff_add(state, goal, operators):
  return ff(state, goal, operators, plan_cost, none, op=sum)[0]
