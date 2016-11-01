import random
from operators import Operator
from states import State, Goal, PartialState
from heapq import heappop, heappush
from collections import deque
from hsp import h_add

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

def achieves(operator, (var, val)):
  return var in operator.effects and operator.effects[var] == val

def induces_cycle(operator, goal, constraints):
  return any((goal, atom) in constraints for atom in operator.cond())

# TODO - sorted self.agenda that allows refinement in different order
# TODO - don't revisit the start state
# TODO - heuristics can be the relaxed plan

class PartialPlan(object):
  def __init__(self, initial, achieved, actions, constraints, agenda, causal_links):
    self.initial = initial
    self.achieved = achieved # TODO - could make this a dict and store achiever
    self.actions = actions
    self.constraints = constraints
    self.agenda = agenda
    self.causal_links = causal_links

  def __str__(self):
    return ("achieved: " + str(self.achieved)+
        "\nactions: " + str(self.actions)+
        "\nconstraints: " + str(self.constraints)+
        "\nagenda: " + str(self.agenda)+
        "\ncausal_links:" + str(self.causal_links))

  def __repr__(self):
    return str((len(self.actions), len(self.constraints), len(self.agenda), len(self.causal_links)))

  def extract_plan(self):
    reached = {g for operator, g in self.causal_links if operator is None}
    other_acts = set(self.actions)
    sorted_acts = []
    while other_acts:
      o1 = random.choice([operator for operator in other_acts if all(condition in reached for condition in operator.cond())])
      other_acts.remove(o1)
      sorted_acts.append(o1)
      reached |= {g for o2, g in self.causal_links if o2 == o1}
    return sorted_acts

  def unsatisfied_goals(self):
    return len(self.agenda)

  def length(self):
    return len(self.actions)

  def cost(self):
    return sum(operator.cost for operator in self.actions)

  def solved(self):
    return self.agenda == []

  def neighbors(self, operators):
    if self.agenda:
      subgoal = self.agenda[0] # TODO - sort the goals
      remaining_agenda = self.agenda[1:]
      for operator in operators:
        if achieves(operator, subgoal) and not induces_cycle(operator, subgoal, self.constraints):
          new_achieved = self.achieved | {subgoal}
          new_actions = self.actions | {operator}
          new_causal_links = self.causal_links + [(operator, subgoal)]

          new_agenda = remaining_agenda[:]
          for condition in operator.cond():
            if condition not in new_achieved and condition not in new_agenda:
              if self.initial[condition[0]] == condition[1]:
                new_achieved.add(condition)
                new_causal_links += [(None, condition)]
              else:
                new_agenda.append(condition)

          consts = self.constraints
          for condition in operator.cond():
            consts = add_constraint((condition, subgoal), consts)
          yield PartialPlan(self.initial,
                            new_achieved,
                            new_actions,
                            consts,
                            new_agenda,
                            new_causal_links)

# TODO - way of weighting the partial order planning progress

def get_initial_plan(initial, goal):
  achieved = {atom for atom in initial.values.items()}
  agenda = []
  for condition in goal.cond():
    if condition not in achieved:
      if initial[condition[0]] == condition[1]:
        achieved.add(condition)
      else:
        agenda.append(condition)
  return PartialPlan(initial, achieved, set(), set(), agenda, [(None, atom) for atom in achieved])


from misc.priority_queue import Queue, FIFOPriorityQueue

def relaxed_pop(initial, goal, operators, QueueClass=FIFOPriorityQueue):
  initial_plan = get_initial_plan(initial, goal)
  #operators.sort()
  iterations = 0
  expanded = 1

  #priority_fn = lambda p: p.length() # NOTE - super slow
  #priority_fn = lambda p: p.length() + p.unsatisfied_goals()
  priority_fn = lambda p: p.unsatisfied_goals()

  if initial_plan.solved():
    return initial_plan.extract_plan(), (iterations, expanded)

  queue = QueueClass()
  queue.push(priority_fn(initial_plan), initial_plan)
  while queue:
    plan = queue.pop()
    print iterations, expanded, plan.length(), plan.unsatisfied_goals(), priority_fn(plan)
    iterations += 1
    for new_plan in plan.neighbors(operators):
      expanded += 1
      if new_plan.solved():
        return new_plan.extract_plan(), (iterations, expanded)
      queue.push(priority_fn(new_plan), new_plan)
  return None, (iterations, expanded)
