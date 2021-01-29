from misc.functions import elapsed_time, first
from misc.priority_queue import FILOPriorityQueue, FIFOPriorityQueue
from planner.state_space import StateSpace


def semideferred_best_first_search(start, goal, generator, priority, stack, max_time, max_iterations,
                                   max_generations, max_cost, max_length, debug):
  # TODO: variants that don't add states to the search queue until parent revisited
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
    for i, nv in enumerate(successors):
      if nv.generate():
        queue.push(priority(nv), nv) # own priority
        if priority(nv) < priority(cv):
          for dv in successors[i+1:]:
            queue.push(priority(cv), dv) # parent priority
          break
  return None, state_space