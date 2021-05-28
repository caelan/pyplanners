from .progression import *
from .meta import *
from misc.utils import *

def simple_debug(vertex): # TODO - pipe planner output to file/stdout
  print('{state_space}{vertex}\n'.format(state_space=vertex.state_space, vertex=vertex))

def pause_debug(vertex):
  simple_debug(vertex)
  user_input('Hit enter to continue')
  print()

###########################################################################

def path_cost_fn(vertex):
  return vertex.cost

def greedy_cost_fn(vertex):
  return vertex.h_cost

def weighted_cost_fn(alpha):
  return lambda vertex: (1 - alpha) * vertex.cost + alpha * vertex.h_cost

###########################################################################

def default_search(search=False, debug=False):
  # hill_climbing_search | deferred_best_first_search | best_first_search | bfs | dfs
  # srandom_walk | srrt | rbfs | rdfs | random_walk | rrt
  if search is False:
    search = deferred_best_first_search
  max_time = max_iterations = max_generations = max_cost = max_length = INF
  if debug is False:
    debug = simple_debug # simple_debug | None

  # TODO - return associated parameters by integrating with Function
  if search == hill_climbing_search:
    cost_step = None
    strategy = strategies.LOCAL
    recurrence = 1
    steepest = False
    max_generations = 1 # TODO - UNDO THIS!
    return lambda start, goal, generator: search(start, goal, generator,
        cost_step, strategy, recurrence, steepest, max_time, max_iterations, max_generations, max_cost, max_length, debug)

  # TODO: be careful about the argument ordering
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
