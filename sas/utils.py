import time

from misc.utils import INF, randomize
#from .set_additive import *
from sas.downward import Problem
from .ff import filter_axioms, in_add, ff_fn, plan_cost, first_combine
from planner.progression import deferred_best_first_search

def h_0(state, goal, operators):
  return 0
def h_naive(state, goal, operators):
  return sum(1 for var, value in goal.cond() if state[var] != value)
def h_blind(state, goal, operators):
  return min(operator.cost for operator in ha_applicable(state, goal, operators))

###########################################################################

def ha_all(state, goal, operators):
  return filter_axioms(operators)
def ha_applicable(state, goal, operators):
  return filter_axioms([operator for operator in operators if operator(state) is not None])
def ha_all_random(state, goal, operators):
  return randomize(ha_all(state, goal, operators))
def ha_applicable_random(state, goal, operators):
  return randomize(ha_applicable(state, goal, operators))
def ha_sorted(state, goal, operators):
  return sorted(ha_applicable(state, goal, operators), key=lambda o: o.cost)

def ha_combine(state, goal, operators, *helpful_actions):
  seen_operators = set()
  for ha in helpful_actions:
    ha_operators = []
    for operator in ha(state, goal, operators):
      if not in_add(seen_operators, operator):
        ha_operators.append(operator)
    yield ha_operators

###########################################################################

# TODO: custom heuristic

def combine(heuristic, helpful_actions):
  return lambda s, g, o: (heuristic(s, g, o), helpful_actions(s, g, o))

def single_complete_ff(ff):
  def fn(state, goal, operators):
    h, ha = ff(state, goal, operators)
    return h, ha + list(set(ha_applicable(state, goal, operators)) - set(ha))
  return fn

def multi_complete_ff(ff):
  def fn(state, goal, operators):
    h, ha = ff(state, goal, operators)
    yield h, ha
    yield h, set(ha_applicable(state, goal, operators)) - set(ha)
  return fn

# TODO - the original operator order is affecting things a lot
# NOTE - expensive to do sa for many successsors (the union operation)
#default_successors = combine(h_0, ha_applicable_random)
#default_successors = combine(h_level, ha_applicable_random)
#default_successors = combine(h_sa, ha_applicable_random)
default_successors = ff_fn(plan_cost, first_combine, op=sum)
#default_successors = sa_fn(sa_first_operators) # sa_first_goals | sa_first_operators | sa_first_combine

###########################################################################

def single_generator(initial, goal, operators, successors):
  #return lambda v: (yield successors(v.state, goal, operators))
  return lambda v: iter([successors(v.state, goal, operators)])

def multi_generator(initial, goal, operators, successors):
  return lambda v: iter(successors(v.state, goal, operators))

default_generator = lambda i, g, o: single_generator(i, g, o, default_successors)

###########################################################################

from .downward import solve_sas

def downward_plan(initial, goal, operators):
  # TODO: relax effects and perform a lazy greedy search
  t0 = time.time()
  problem = Problem(initial, goal, operators, [])
  return solve_sas(problem), time.time() - t0

###########################################################################

#default_search = default_plan
#default_search = lambda initial, goal, generator: bfs(initial, goal, generator, INF, INF, INF, INF, INF, None)
#default_search = lambda initial, goal, generator: a_star_search(initial, goal, generator,
#        lambda v: v.cost, False, INF, INF, INF, INF, INF, None)
#default_search = lambda initial, goal, generator: a_star_search(initial, goal, generator,
#        lambda v: v.cost + v.h_cost, True, INF, INF, INF, INF, INF, None)
#default_search = lambda initial, goal, generator: best_first_search(initial, goal, generator,
#        lambda v: v.h_cost, False, INF, INF, INF, INF, INF, None)
default_search = lambda initial, goal, generator: deferred_best_first_search(initial, goal, generator,
        lambda v: v.h_cost, stack=False, max_time=INF, max_iterations=INF, debug=None) # True vs False can matter quite a bit
#default_search = lambda initial, goal, generator: semideferred_best_first_search(initial, goal, generator,
#        lambda v: v.h_cost, True, INF, INF, INF, INF, INF, None) # True vs False can matter quite a bit
#default_search = lambda initial, goal, generator: hill_climbing_search(initial, goal, generator,
#        None, 0, 1, False, INF, INF, INF, INF, INF, None)

def default_plan(initial, goal, operators):
  return default_search(initial, goal, default_generator(initial, goal, operators))

def default_derived_plan(initial, goal, operators, axioms):
  return default_search(initial, goal, (
    lambda v: iter([default_successors(v.state, goal, operators + axioms)]), axioms))
