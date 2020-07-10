from ..state_space import StateSpace
from misc.numerical import INF
from misc.functions import reverse, elapsed_time, first
from misc.priority_queue import FIFOClassicPriorityQueue, FILOClassicPriorityQueue, FIFOPriorityQueue, FILOPriorityQueue

# TODO - Update the shortest path using Bellman-Ford if find shorter path to previously visited state
# NOTE - Best first searches with infinite branching factors are not complete. Need to use iterative deepening on max_expansions and max_length

def weighted(weight):
    if weight == INF:
        return lambda v: (v.h_cost, v.cost)
    return lambda v: (v.cost + weight * v.h_cost)

uniform = weighted(0)
astar = weighted(1)
wastar2 = weighted(2)
wastar3 = weighted(2)
greedy = weighted(INF)

###########################################################################

# TODO: deprecate

def path_cost_fn(vertex):
  return vertex.cost

def greedy_cost_fn(vertex):
  return vertex.h_cost

def weighted_cost_fn(alpha):
  return lambda vertex: (1 - alpha) * vertex.cost + alpha * vertex.h_cost

###########################################################################

def check_test(vertex):
  if vertex.parent_edge is None:
    return True
  parent_state = vertex.parent_edge.source.state
  parent_op = vertex.parent_edge.operator
  valid = parent_op.test(parent_state) # TODO: hasattr
  if not valid:
    vertex.disconnect()
  return valid

###########################################################################

def a_star_search(start, goal, generator, priority, stack=False,
                  max_time=INF, max_iterations=INF, max_generations=INF,
                  max_cost=INF, max_length=INF, debug=None):
  state_space = StateSpace(generator, start, INF, max_generations, max_cost, max_length)
  sv = state_space.root
  if sv.contained(goal):
    return state_space.plan(sv), state_space
  if not sv.generate():
    return None, state_space
  queue = (FILOClassicPriorityQueue if stack else FIFOClassicPriorityQueue)([(priority(sv), sv)])
  while not queue.empty() and (elapsed_time(state_space.start_time) < max_time) \
          and (state_space.iterations < max_iterations):
    cv = queue.pop()
    state_space.iterations += 1
    if debug is not None:
      debug(cv)
    if cv.contained(goal):
      return state_space.plan(cv), state_space
    while cv.generate():
      pass # NOTE - A* is not optimal even for an admissible heuristic if you allow re-expansion of branches
    if cv.h_cost is None:
      break
    for v in (reverse(cv.unexplored()) if stack else cv.unexplored()):
      if v.generate():
        queue.decrease_key(priority(v), v)
  return None, state_space

def best_first_search(start, goal, generator, priority, stack=False, lazy=True,
                      max_time=INF, max_iterations=INF, max_generations=INF,
                      max_cost=INF, max_length=INF, debug=None):
  state_space = StateSpace(generator, start, 1, max_generations, max_cost, max_length)
  sv = state_space.root
  sv.generate()
  if sv.is_dead_end():
    return None, state_space
  queue = (FILOPriorityQueue if stack else FIFOPriorityQueue)([(priority(sv), sv)])
  while not queue.empty() and (elapsed_time(state_space.start_time) < max_time) \
          and (state_space.iterations < max_iterations):
    state_space.iterations += 1
    cv = queue.pop()
    if lazy and not check_test(cv):
      continue
    if debug is not None:
      debug(cv)
    if cv.contained(goal):
      return state_space.plan(cv), state_space
    successors = list(cv.unexplored())
    if not cv.enumerated():
      successors.append(cv)
    for v in (reversed(successors) if stack else successors):
      v.generate() # Also evaluates the h_cost
      if (not v.is_dead_end()) and (lazy or check_test(v)):
        queue.push(priority(v), v)
  return None, state_space

def deferred_best_first_search(start, goal, generator, priority, stack=False,
                               max_time=INF, max_iterations=INF, max_generations=INF,
                               max_cost=INF, max_length=INF, debug=None):
  state_space = StateSpace(generator, start, 1, max_generations, max_cost, max_length)
  queue = (FILOPriorityQueue if stack else FIFOPriorityQueue)([(None, state_space.root)])
  while not queue.empty() and (elapsed_time(state_space.start_time) < max_time) \
          and (state_space.iterations < max_iterations):
    state_space.iterations += 1
    cv = queue.pop()
    if not check_test(cv):
      continue
    if debug is not None:
      debug(cv)
    if cv.contained(goal):
      return state_space.plan(cv), state_space
    cv.generate()
    if cv.is_dead_end():
        continue
    h = priority(cv)
    successors = list(cv.unexplored())
    if not cv.enumerated():
      successors.append(cv) # TODO: use its prior value
    for v in (reversed(successors) if stack else successors):
      queue.push(h, v) # TODO: combine with the action cost
  return None, state_space

###########################################################################

def macro_greedy_cost_fn(v):
  if v.parent_edge is None:
    return v.h_cost
  return v.parent_edge.source.h_cost - len(v.parent_edge.operator)

def macro_deferred_best_first_search(start, goal, generator, priority, stack, max_time, max_iterations,
                                     max_generations, max_cost, max_length, debug):
  state_space = StateSpace(generator, start, 1, max_generations, max_cost, max_length)
  sv = state_space.root
  if sv.contained(goal):
    return state_space.plan(sv), state_space
  queue = (FILOPriorityQueue if stack else FIFOPriorityQueue)([(None, sv)])
  while not queue.empty() and (elapsed_time(state_space.start_time) < max_time) \
          and (state_space.iterations < max_iterations):
    cv = queue.pop()
    if not cv.generate():
      continue
    state_space.iterations += 1
    if debug is not None:
      debug(cv)
    successors = list(cv.unexplored()) + [cv]
    gv = first(lambda v: v.contained(goal), successors[:-1])
    if gv is not None:
      return state_space.plan(gv), state_space
    for v in (reversed(successors) if stack else successors):
      queue.push(priority(v), v)
  return None, state_space

###########################################################################

# TODO - variants that don't add states to the search queue until parent revisited
def semideferred_best_first_search(start, goal, generator, priority, stack, max_time, max_iterations,
                                   max_generations, max_cost, max_length, debug):
  state_space = StateSpace(generator, start, 1, max_generations, max_cost, max_length)
  sv = state_space.root
  if sv.contained(goal):
    return state_space.plan(sv), state_space
  queue = (FILOPriorityQueue if stack else FIFOPriorityQueue)([(None, sv)])
  while not queue.empty() and (elapsed_time(state_space.start_time) < max_time) \
          and (state_space.iterations < max_iterations):
    cv = queue.pop()
    if not cv.has_unexplored() and not cv.generate():
      continue
    state_space.iterations += 1
    if debug is not None:
      debug(cv)
    successors = list(cv.unexplored()) + [cv]
    gv = first(lambda v: v.contained(goal), successors[:-1])
    if gv is not None:
      return state_space.plan(gv), state_space
    if stack:
      successors.reverse()
    for i, v in enumerate(successors):
      if v.generate():
        queue.push(priority(v), v)
        if priority(v) < priority(cv):
          for dv in successors[i+1:]:
            queue.push(priority(cv), dv)
          break
  return None, state_space
