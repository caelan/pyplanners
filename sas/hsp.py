from misc.utils import *

Node = namedtuple('Node', ['cost', 'level'])

# Record parent operator for values to even more efficiently linearize
# TODO - helpful actions

def compute_costs(state, goal, operators, op=max, unit=False, greedy=True):
  variable_nodes = defaultdict(dict)
  operator_nodes = {}
  conditions = defaultdict(lambda: defaultdict(set))
  unsatisfied = {}
  queue = []

  def applicable_operator(operator):
    if len(operator.conditions) != 0:
      operator_nodes[operator] = Node(op(variable_nodes[v][val].cost for v, val in operator.cond()),
          max(variable_nodes[v][val].level for v, val in operator.cond()))
    else:
      operator_nodes[operator] = Node(0, 0)
    if operator != goal:
      variable_node = Node(operator_nodes[operator].cost + (operator.cost if not unit else 1),
          operator_nodes[operator].level + 1)
      for var2, value2 in operator.eff():
        if value2 not in variable_nodes[var2] or variable_node < variable_nodes[var2][value2]:
          variable_nodes[var2][value2] = variable_node
          heappush(queue, (variable_node, var2, value2))

  for operator in operators + [goal]:
    unsatisfied[operator] = len(operator.conditions)
    for var, value in operator.cond(): # TODO - store this in memory
      conditions[var][value].add(operator)
    if unsatisfied[operator] == 0:
      applicable_operator(operator)
      if greedy and operator == goal:
        return variable_nodes, operator_nodes
  for var in conditions:
    for value in conditions[var]:
      if state[var] == value:
        variable_nodes[var][value] = Node(0, 0)
        queue.append((0, var, value))

  processed = defaultdict(set)
  while len(queue) != 0:
    _, var, value = heappop(queue)
    if value in processed[var]: continue
    processed[var].add(value)

    for operator in conditions[var][value]:
      unsatisfied[operator] -= 1
      if unsatisfied[operator] == 0:
        applicable_operator(operator)
        if greedy and operator == goal:
          return variable_nodes, operator_nodes
  return variable_nodes, operator_nodes

###########################################################################

# NOTE - can also be equivalently done as compute_costs with a deque
# TODO - method for converting into levels into nodes for FF

def relaxed_plan_graph(state, goal, operators, greedy=True): # NOTE - Slightly faster than unit compute_costs (0.002 vs 0.005(
  variable_levels = defaultdict(dict)
  operator_levels = {}
  conditions = defaultdict(lambda: defaultdict(list))
  unsatisfied = {}
  next_operators = []

  def update_unsatisfied(var, value):
    for operator in conditions[var][value]:
      unsatisfied[operator] -= 1
      if unsatisfied[operator] == 0:
        next_operators.append(operator)

  for operator in operators + [goal]:
    unsatisfied[operator] = len(operator.conditions)
    for var, value in operator.cond(): # TODO - store this in memory
      conditions[var][value].append(operator)
    if unsatisfied[operator] == 0:
      next_operators.append(operator)
  for var in conditions:
    for value in conditions[var]:
      if state[var] == value:
        variable_levels[var][value] = 0
        update_unsatisfied(var, value)

  for level in irange(INF):
    current_operators = next_operators[:]
    next_operators = []
    for operator in current_operators:
      operator_levels[operator] = level
      if operator == goal:
        if greedy: return operator_levels, variable_levels
        continue
      for var, value in operator.eff():
        if value not in variable_levels[var] :
          variable_levels[var][value] = level + 1
          update_unsatisfied(var, value)
    if len(next_operators) == 0:
      break
  return operator_levels, variable_levels

###########################################################################

def h_add(state, goal, operators):
  _, operator_costs = compute_costs(state, goal, operators, op=sum)
  return operator_costs[goal].cost if goal in operator_costs else None

def h_max(state, goal, operators):
  _, operator_costs = compute_costs(state, goal, operators, op=max)
  return operator_costs[goal].cost if goal in operator_costs else None

def h_add_unit(state, goal, operators):
  _, operator_costs = compute_costs(state, goal, operators, op=sum, unit=True)
  return operator_costs[goal].cost if goal in operator_costs else None

def h_max_unit(state, goal, operators):
  _, operator_costs = compute_costs(state, goal, operators, op=max, unit=True)
  return operator_costs[goal].cost if goal in operator_costs else None

def h_level(state, goal, operators): # = h_max with unit costs
  return relaxed_plan_graph(state, goal, operators)[0].get(goal, None)
