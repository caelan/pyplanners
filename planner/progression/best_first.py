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

def test_goal(vertex, goal):
  if not vertex.contained(goal):
    return False
  if not hasattr(goal, 'test'):
    return True
  return goal.test(vertex.state)

def test_parent_operator(sink_vertex):
  parent_edge = sink_vertex.parent_edge
  if parent_edge is None:
    return True
  parent_op = parent_edge.operator
  if not hasattr(parent_op, 'test'):
    return True
  parent_state = parent_edge.source.state
  # TODO: apply external functions
  if parent_op.test(parent_state):
    return True
  return False

def order_successors(successors, stack=False):
    return reversed(successors) if stack else successors

###########################################################################

def a_star_search(start, goal, generator, priority, stack=False,
                  max_time=INF, max_iterations=INF, debug=None, **kwargs):
  # TODO: update to use test_parent_operator
  state_space = StateSpace(generator, start, max_extensions=INF, **kwargs)
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
    if test_goal(cv, goal):
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
                      max_time=INF, max_iterations=INF, debug=None, **kwargs):
  state_space = StateSpace(generator, start, max_extensions=1, **kwargs)
  sv = state_space.root
  sv.generate()
  if sv.is_dead_end():
    return None, state_space
  queue = (FILOPriorityQueue if stack else FIFOPriorityQueue)([(priority(sv), sv)])
  while not queue.empty() and (elapsed_time(state_space.start_time) < max_time) \
          and (state_space.iterations < max_iterations):
    state_space.iterations += 1
    cv = queue.pop()
    if lazy and not test_parent_operator(cv):
      continue
    if debug is not None:
      debug(cv)
    if test_goal(cv, goal):
      return state_space.plan(cv), state_space
    successors = list(cv.unexplored())
    if not cv.enumerated():
      successors.append(cv)
    for v in order_successors(successors, stack):
      v.generate() # Also evaluates the h_cost
      if (not v.is_dead_end()) and (lazy or test_parent_operator(v)):
        queue.push(priority(v), v)
  return None, state_space

def deferred_best_first_search(start, goal, generator, priority, stack=False,
                               max_time=INF, max_iterations=INF, debug=None, **kwargs):
  state_space = StateSpace(generator, start, max_extensions=1, **kwargs)
  queue = (FILOPriorityQueue if stack else FIFOPriorityQueue)([(None, state_space.root)])
  while not queue.empty() and (elapsed_time(state_space.start_time) < max_time) \
          and (state_space.iterations < max_iterations):
    state_space.iterations += 1
    cv = queue.pop()
    if not test_parent_operator(cv):
      continue
    if debug is not None:
      debug(cv)
    if test_goal(cv, goal):
      return state_space.plan(cv), state_space
    cv.generate()
    if cv.is_dead_end():
        continue
    h = priority(cv) # TODO: incorporate the path cost of v instead of cv
    successors = list(cv.unexplored())
    if not cv.enumerated():
      successors.append(cv) # TODO: use its prior value
    for v in order_successors(successors, stack):
      queue.push(h, v) # TODO: combine with the action cost
  return None, state_space

###########################################################################

def macro_greedy_cost_fn(v):
  # TODO: only want to perform this if the macro is helpful
  if v.parent_edge is None:
    return v.h_cost
  return v.parent_edge.source.h_cost - len(v.parent_edge.operator)

def macro_deferred_best_first_search(start, goal, generator, priority, stack=False,
                                     max_time=INF, max_iterations=INF, debug=None, **kwargs):
  state_space = StateSpace(generator, start, max_extensions=1, **kwargs)
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
    for v in order_successors(successors, stack):
      queue.push(priority(v), v)
  return None, state_space

###########################################################################

# TODO - variants that don't add states to the search queue until parent revisited
# def semideferred_best_first_search(start, goal, generator, priority, stack, max_time, max_iterations,
#                                    max_generations, max_cost, max_length, debug):
#   state_space = StateSpace(generator, start, 1, max_generations, max_cost, max_length)
#   sv = state_space.root
#   if sv.contained(goal):
#     return state_space.plan(sv), state_space
#   queue = (FILOPriorityQueue if stack else FIFOPriorityQueue)([(None, sv)])
#   while not queue.empty() and (elapsed_time(state_space.start_time) < max_time) \
#           and (state_space.iterations < max_iterations):
#     cv = queue.pop()
#     if not cv.has_unexplored() and not cv.generate():
#       continue
#     state_space.iterations += 1
#     if debug is not None:
#       debug(cv)
#     successors = list(cv.unexplored()) + [cv]
#     gv = first(lambda v: v.contained(goal), successors[:-1])
#     if gv is not None:
#       return state_space.plan(gv), state_space
#     if stack:
#       successors.reverse()
#     for i, v in enumerate(successors):
#       if v.generate():
#         queue.push(priority(v), v)
#         if priority(v) < priority(cv):
#           for dv in successors[i+1:]:
#             queue.push(priority(cv), dv)
#           break
#   return None, state_space
