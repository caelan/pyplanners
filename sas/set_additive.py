from misc.utils import *
from misc.priority_queue import PriorityQueue

Node = namedtuple('Node', ['cost', 'operators'])

"""
class Node(Set, object):
  def __init__(self, operators):
    self.operators = operators
    self.cost = self._cost()
  def __contains__(self, operator):
    return operator in self.operators
  def __iter__(self):
    return iter(self.operators)
  def __len__(self):
    return len(self.operators)
  def _cost(self):
    return sum(operator.cost for operator in self.operators)

# https://docs.python.org/2/library/stdtypes.html#set.union
# set.union
class UnitNode(Node):
  def _cost(self):
    return len(self.operators)
"""

# TODO - merge process that attempts to reason about operators that accomplish each others goals by extending union

def relaxed_plan(state, goal, operators, unit=False, greedy=True):
  variable_nodes = defaultdict(dict)
  operator_nodes = {}
  conditions = defaultdict(lambda: defaultdict(list))
  unsatisfied = {}
  queue = PriorityQueue()

  def union(nodes):
    operators = set(flatten(node.operators for node in nodes))
    cost = sum(operator.cost for operator in operators) if not unit else len(operators)
    return Node(cost, operators)

  def applicable_operator(operator):
    operator_nodes[operator] = union(variable_nodes[v][val] for v, val in operator.cond())
    if operator != goal:
      variable_node = union([operator_nodes[operator], Node(None, {operator})])
      for var2, value2 in operator.eff():
        if value2 not in variable_nodes[var2] or variable_node.cost < variable_nodes[var2][value2].cost:
          variable_nodes[var2][value2] = variable_node
          queue.push(variable_node.cost, (var2, value2))

  for operator in operators + [goal]:
    unsatisfied[operator] = len(operator.conditions)
    for var, value in operator.cond(): # TODO - store this in memory
      conditions[var][value].append(operator)
    if unsatisfied[operator] == 0:
      applicable_operator(operator)
      if greedy and operator == goal:
        return operator_nodes, variable_nodes
  for var in conditions:
    for value in conditions[var]:
      if state[var] == value:
        variable_nodes[var][value] = Node(0, {})
        queue.push(variable_nodes[var][value].cost, (var, value))

  processed = defaultdict(set)
  while not queue.empty():
    var, value = queue.pop()
    if value in processed[var]: continue
    processed[var].add(value)

    for operator in conditions[var][value]:
      unsatisfied[operator] -= 1
      if unsatisfied[operator] == 0:
        applicable_operator(operator)
        if greedy and operator == goal:
          return operator_nodes, variable_nodes
  return operator_nodes, variable_nodes

# TODO - propagate relaxed plan backwards to find goals

def none(*args):
  return []

def applicable(goal, operator_nodes, *args):
  return list(filter(lambda o: len(operator_nodes[o].operators) == 0, operator_nodes))

def any_goals(goal, operator_nodes, variable_nodes):
  goals = set(flatten(o.cond() for o in (operator_nodes[goal].operators | {goal})))
  return list(filter(lambda o: any(e in goals for e in o.eff()), applicable(goal, operator_nodes, variable_nodes)))

def first_goals(goal, operator_nodes, variable_nodes):
  goals = list(filter(lambda item: len(variable_nodes[item[0]][item[1]].operators) == 1,
                      set(flatten(o.cond() for o in (operator_nodes[goal].operators | {goal})))))
  return list(filter(lambda o: o != goal and any(e in goals for e in o.eff()),
                     applicable(goal, operator_nodes, variable_nodes)))

def first_operators(goal, operator_nodes,  *args):
  return [operator for operator in operator_nodes[goal].operators if len(operator_nodes[operator].operators) == 0]

def first_combine(goal, operator_nodes, variable_nodes):
  one = first_operators(goal, operator_nodes, variable_nodes)
  two = first_goals(goal, operator_nodes, variable_nodes) # TODO - include applicable
  return list(one) + list(set(two) - set(one))

def sa(state, goal, operators, helpful_actions, unit=False):
  operator_nodes, variable_nodes = relaxed_plan(state, goal, operators, unit=unit)
  if goal not in operator_nodes: return None, []
  return operator_nodes[goal].cost, helpful_actions(goal, operator_nodes, variable_nodes)

def sa_fn(helpful_actions, unit=False):
  return lambda s, g, o: sa(s, g, o, helpful_actions, unit=unit)

def h_sa(state, goal, operators):
  operator_costs = relaxed_plan(state, goal, operators)[0]
  return operator_costs[goal].cost if goal in operator_costs else None

def h_sa_unit(state, goal, operators):
  operator_costs = relaxed_plan(state, goal, operators, unit=True)[0]
  return operator_costs[goal].cost if goal in operator_costs else None
