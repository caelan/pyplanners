from .progression import *
from .meta import *
#from .reachability_graph.relaxed_plan_graph import RelaxedPlanGraph
from .connectivity_graph.relaxed_connectivity_graph import RelaxedConnectivityGraph
from planner.heuristics import h_ff_add
from planner.helpful_actions import ha_applicable_macro, ha_level_goal_macro_sorted, ha_relaxed_plan_goal_macro, ha_relaxed_plan_action_macro, \
  ha_relaxed_plan_goal_macro_sorted, ha_relaxed_plan_action_macro_sorted, ha_achieving_macro_sorted
from .generators import reachability_generator, connectivity_generator
from misc.utils import *

def simple_debug(vertex): # TODO - pipe planner output to file/stdout
  print('{state_space}{vertex}\n'.format(state_space=vertex.state_space, vertex=vertex))

def pause_debug(vertex):
  simple_debug(vertex)
  user_input('Hit enter to continue')
  print()

"""
def redo_scheduler_generator(goal, Scheduler):
  reachability_graph = RelaxedPlanGraph
  heuristic = h_ff_add
  helpful_actions = ha_relaxed_plan_action_macro_sorted
  max_time = INF
  max_iterations = INF
  max_cycles = INF
  return lambda vertex: reachability_generator(vertex, reachability_graph(vertex.state, goal, Scheduler),
      heuristic, helpful_actions, max_time=max_time, max_iterations=max_iterations, max_cycles=max_cycles) # TODO - clean up scheduler
    #special_reachability_generator(vertex, reachability_graph(vertex.state, goal, Scheduler), heuristic, helpful_actions)
"""

#def reuse_scheduler_generator(goal, Scheduler):
def default_scheduler_generator(goal, Scheduler):
  connectivity_graph = RelaxedConnectivityGraph(goal, Scheduler)
  heuristic = h_ff_add
  helpful_actions = ha_achieving_macro_sorted # ha_relaxed_plan_action_macro_sorted | ha_achieving_macro_sorted
  max_time = INF
  max_iterations = INF
  max_cycles = INF
  max_generations = INF
  greedy = False
  return lambda vertex: connectivity_generator(vertex, connectivity_graph, heuristic, helpful_actions,
      max_time=max_time, max_iterations=max_iterations, max_cycles=max_cycles, max_generations=max_generations, greedy=greedy)

def default_search(search=False, debug=False):
  if search is False: search = deferred_best_first_search # hill_climbing_search | deferred_best_first_search | best_first_search | bfs | dfs | srandom_walk | srrt | rbfs | rdfs | random_walk | rrt
  max_time = INF
  max_iterations = INF
  max_generations = INF
  max_cost = INF
  max_length = INF
  if debug is False: debug = simple_debug # simple_debug | None

  # TODO - return associated parameters by integrating with Function
  if search == hill_climbing_search:
    cost_step = None
    strategy = strategies.LOCAL
    recurrence = 1
    steepest = False
    max_generations = 1 # TODO - UNDO THIS!
    return lambda start, goal, generator: search(start, goal, generator,
        cost_step, strategy, recurrence, steepest, max_time, max_iterations, max_generations, max_cost, max_length, debug)

  if search == a_star_search:
    max_generations = 1
    cost_fn = weighted_cost_fn(.5) # path_cost_fn
    stack = False
    return lambda start, goal, generator: search(start, goal, generator,
        cost_fn, stack, max_time, max_iterations, max_generations, max_cost, max_length, debug)

  if search == best_first_search:
    max_generations = 1
    cost_fn = greedy_cost_fn
    stack = False
    return lambda start, goal, generator: search(start, goal, generator,
        cost_fn, stack, max_time, max_iterations, max_generations, max_cost, max_length, debug)

  if search == deferred_best_first_search:
    max_generations = 1
    cost_fn = greedy_cost_fn
    stack = False
    return lambda start, goal, generator: search(start, goal, generator,
        cost_fn, stack, max_time, max_iterations, max_generations, max_cost, max_length, debug)

  if search == macro_deferred_best_first_search:
    max_generations = 1
    cost_fn = macro_greedy_cost_fn
    stack = False
    return lambda start, goal, generator: search(start, goal, generator,
        cost_fn, stack, max_time, max_iterations, max_generations, max_cost, max_length, debug)

  if search in [bfs, srandom_walk]:
    max_generations = 1
    return lambda start, goal, generator: search(start, goal, generator,
        max_time, max_iterations, max_generations, max_cost, max_length, debug)

  if search == dfs:
    max_generations = 1
    max_length = 20
    return lambda start, goal, generator: search(start, goal, generator,
        max_time, max_iterations, max_generations, max_cost, max_length, debug)

  if search in [rbfs, random_walk]:
    recurrence = 1
    return lambda start, goal, generator: search(start, goal, generator,
        recurrence, max_time, max_iterations, max_generations, max_cost, max_length, debug)

  if search == rdfs:
    recurrence = 1
    max_generations = 1
    max_length = 20
    return lambda start, goal, generator: search(start, goal, generator,
        recurrence, max_time, max_iterations, max_generations, max_cost, max_length, debug)

  raise ValueError('Invalid search: ' + str(search))

def default_meta(meta=incremental_goal_addition): # incremental_goal_addition
  if meta == incremental_goal_addition:
    return lambda start, goal, generator, search: meta(start, goal, lambda s, g: search(s, g, generator))

  raise ValueError('Invalid meta: ' + str(meta))

def default_plan(start, goal, generator, search=False, meta=None, debug=False):
  search = default_search(search, debug)
  if meta is not None:
    meta = default_meta(meta)
    return meta(start, goal, generator, search)
  return search(start, goal, generator)
