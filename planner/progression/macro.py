from misc.functions import elapsed_time, first
from misc.numerical import INF
from misc.priority_queue import FILOPriorityQueue, FIFOPriorityQueue
from planner.progression.best_first import order_successors
from planner.state_space import StateSpace


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
    for nv in order_successors(successors, stack):
      queue.push(priority(nv), nv)
  return None, state_space