import random
from operators import Operator
from states import State, Goal, PartialState
from heapq import heappop, heappush
from collections import deque
from hsp import h_add, h_max

class GoalConditions(PartialState):
  def __init__(self, conditions): # Difference is that this is a list
    self.conditions = conditions
  def cond(self):
    return self.conditions
  #def __contains__(self, state):
  #  return all(state[var] == value for var, value in self.cond())

class UniqueOperator(object):
  next_index = 0
  def __init__(self, action):
    self.action = action
    self.index = UniqueOperator.next_index
    UniqueOperator.next_index += 1
  def __repr__(self):
    return str(self.action) + '#' + str(self.index)

#def effects(action):
#  if isinstance(action, Operator):
#    return action.effects
#  if isinstance(action, State):
#    return action.values # TODO - should include default false values
#  if isinstance(action, Goal):
#    return {}
#  raise ValueError(action)

def achieves(operator, item):
  (var, val) = item
  if isinstance(operator, Operator):
    return var in operator.effects and operator.effects[var] == val
  if isinstance(operator, UniqueOperator):
    return var in operator.action.effects and operator.action.effects[var] == val
  if isinstance(operator, State):
    return operator[var] == val
  if isinstance(operator, Goal):
    return False
  raise ValueError(operator)
  #return var in effects(action) and effects(action)[var] == val

def deletes(operator, item):
  (var, val) = item
  if isinstance(operator, Operator):
    return var in operator.effects and operator.effects[var] != val
  if isinstance(operator, UniqueOperator):
    return var in operator.action.effects and operator.action.effects[var] != val
  if isinstance(operator, State):
    return operator[var] != val
  if isinstance(operator, Goal):
    return False
  raise ValueError(operator)
  #return var in effects(action) and effects(action)[var] != val

def add_constraint(initial_const, constraints):
  if initial_const in constraints:
    return constraints
  consts = [initial_const] # Transitive constraints
  new_constraints = constraints.copy()
  while consts:
    x0, x1 = consts.pop()
    new_constraints.add((x0, x1))
    for x, y in new_constraints:
      if x == x1 and (x0, y) not in new_constraints:
        consts.append((x0, y))
      if y == x0 and (x, x1) not in new_constraints:
        consts.append((x, x1))
  return new_constraints

def possible(position, constraint):
  (x, y) = position
  return (y,x) not in constraint

def protect_cl_for_actions(actions, constrs, clink):
  """yields constriants that extend constrs and
  protect causal link (a0, subgoal, a1)
  for each action in actions
  """
  if actions:
    a = actions[0]
    rem_actions = actions[1:]
    a0, subgoal, a1 = clink
    if a != a0 and a != a1 and deletes(a,subgoal):
      if possible((a, a0), constrs):
        new_const = add_constraint((a, a0), constrs)
        for c in protect_cl_for_actions(rem_actions, new_const, clink):
          yield c
      if possible((a1, a), constrs):
        new_const = add_constraint((a1, a), constrs)
        for c in protect_cl_for_actions(rem_actions, new_const, clink):
          yield c
    else:
      for c in protect_cl_for_actions(rem_actions,constrs,clink):
        yield c
  else:
    yield constrs

def protect_all_cls(clinks, act, constrs):
  """yields constraints that protect all causal links from act"""
  if clinks:
    a0, cond, a1 = clinks[0]  # select a causal link
    rem_clinks = clinks[1:]   # remaining causal links
    if act != a0 and act != a1 and deletes(act, cond):
      if possible((act, a0), constrs):
        new_const = add_constraint((act, a0), constrs)
        for c in protect_all_cls(rem_clinks, act, new_const):
          yield c
      if possible((a1, act), constrs):
        new_const = add_constraint((a1, act), constrs)
        for c in protect_all_cls(rem_clinks, act, new_const):
          yield c
    else:
      for c in protect_all_cls(rem_clinks, act, constrs):
        yield c
  else:
    yield constrs

# TODO - sorted self.agenda that allows refinement in different order

class PartialPlan(object):
  def __init__(self, actions, constraints, agenda, causal_links):
    """
    * actions is a set of action instances
    * constraints a set of (a0,a1) pairs, representing a0<a1,
      closed under transitivity
    * agenda list of (subgoal,action) pairs to be achieved, where
      subgoal is a (variable,value) pair
    * causal_links is a set of (a0,g,a1) triples,
      where ai are action instances, and g is a (variable,value) pair
    """
    self.actions = actions  # a set of action instances
    self.constraints = constraints  # a set of (a0,a1) pairs
    self.agenda = agenda  # list of (subgoal,action) pairs to be achieved
    self.causal_links = causal_links # set of (a0,g,a1) triples

  def __str__(self):
    return ("actions: " + str(self.actions)+
        "\nconstraints: " + str(self.constraints)+
        "\nagenda: " + str(self.agenda)+
        "\ncausal_links:" + str(self.causal_links))

  def __repr__(self):
    return str((len(self.actions), len(self.constraints), len(self.agenda), len(self.causal_links)))

  def extract_plan(self):
    #print(self)
    other_acts = set(self.actions)
    sorted_acts = []
    while other_acts:
      a = random.choice([a for a in other_acts if all((a1, a) not in self.constraints for a1 in other_acts)])
      other_acts.remove(a)
      if isinstance(a, UniqueOperator):
        sorted_acts.append(a.action)
    return sorted_acts

  def flaws_heuristic(self, *args):
    #return self.goals_heuristic() + # number of threats
    pass

  def goals_heuristic(self, *args):
    return len(self.agenda)

  def add_heursitic(self, operators): # TODO - cache this
    #print(GoalConditions(self.agenda))
    #return h_add(self.actions[0], GoalConditions([g for g, _ in self.agenda]), operators)
    return h_max(self.actions[0], GoalConditions([g for g, _ in self.agenda]), operators)
    #return h_add(self.actions[0], self.actions[1], operators)

  #heuristic = flaws_heuristic
  #heuristic = goals_heuristic
  heuristic = add_heursitic # TODO - add all currently reachable actions?

  def rank(self, operators):
    #return (len(self.actions), len(self.constraints), len(self.agenda), len(self.causal_links))
    return self.length() + self.heuristic(operators)
    #return self.length() + 5*self.heuristic(operators)
    #return self.heuristic(operators)

  def length(self):
    return len(self.actions) - 2

  def cost(self):
    pass

  def solved(self):
    return self.agenda == []

  def neighbors(self, operators):
    if self.agenda:
      subgoal, act1 = self.agenda[0]
      remaining_agenda = self.agenda[1:]
      for act0 in self.actions:
        if achieves(act0, subgoal) and possible((act0, act1), self.constraints):
          consts1 = add_constraint((act0, act1), self.constraints)
          new_clink = (act0, subgoal, act1)
          new_cls = self.causal_links + [new_clink]
          for consts2 in protect_cl_for_actions(self.actions, consts1, new_clink):
            yield PartialPlan(self.actions, consts2, remaining_agenda, new_cls)

      for a0 in operators:
        if achieves(a0, subgoal):
          new_a = UniqueOperator(a0) # This is why these things are wrapped, to allow several of the same actions
          new_actions = self.actions + [new_a]
          consts1 = add_constraint((self.actions[0], new_a), self.constraints)
          consts2 = add_constraint((new_a, act1), consts1) # Goal constraint automatically derived
          new_agenda = remaining_agenda + [(pre, new_a) for pre in a0.cond()] # NOTE - previously was bug that overwrote new_agenda
          new_clink = (new_a, subgoal, act1)
          new_cls = self.causal_links + [new_clink]
          for consts3 in protect_all_cls(self.causal_links, new_a, consts2):
            for consts4 in protect_cl_for_actions(self.actions, consts3, new_clink):
              yield PartialPlan(new_actions, consts4, new_agenda, new_cls)

def pop_solve(initial, goal, operators, max_length=float('inf')):
  initial_plan = PartialPlan([initial, goal],
                         {(initial, goal)},
                         [(g, goal) for g in goal.cond()],
                         [])
  #operators.sort()
  iterations = 0
  expanded = 1
  if initial_plan.solved():
    return initial_plan.extract_plan(), (iterations, expanded)

  BFS = False
  if BFS:
    queue = deque([initial_plan])
  else:
    queue = [(initial_plan.rank(operators), initial_plan)]
  while queue:
    #queue = deque(sorted(queue, key=lambda q: q.rank()))
    if BFS:
      plan = queue.popleft()
    else:
      _, plan = heappop(queue)
    #print(len(queue), sorted(queue, key=lambda q: q.rank()))
    print(iterations, expanded, plan.heuristic(operators), plan.length()) #, len(neighbors)
    #print(plan)
    #raw_input()
    iterations += 1
    for new_plan in plan.neighbors(operators):
      if new_plan.length() > max_length:
        continue
      expanded += 1
      if new_plan.solved():
        return new_plan.extract_plan(), (iterations, expanded)
      if BFS:
        queue.append(new_plan)
      else:
        heappush(queue, (new_plan.rank(operators), new_plan))
  return None, (iterations, expanded)
