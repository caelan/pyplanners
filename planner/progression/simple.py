from .utils import *
from ..state_space import *

def search(pop, start, goal, generator, max_time, max_iterations, max_generations, max_cost, max_length, debug):
  state_space = StateSpace(generator, start, 1, max_generations, max_cost, max_length)
  sv = state_space.root
  if sv.contained(goal): return state_space.plan(sv), state_space
  queue = deque([sv])
  while len(queue) > 0 and time() - state_space.start_time < max_time and state_space.iterations < max_iterations:
    cv = pop(queue)
    state_space.iterations += 1
    if debug is not None: debug(cv)

    while cv.generate(): pass
    if cv.h_cost is None: break
    for nv in cv.unexplored(): # TODO - should reverse order for DFS
      if nv.contained(goal):
        return state_space.plan(nv), state_space
      queue.append(nv)
  return None, state_space

def dfs(*args):
  return search(lambda queue: queue.pop(), *args)

def bfs(*args):
  return search(lambda queue: queue.popleft(), *args)

def srandom_walk(*args):
  return search(pop_random, *args)

def srrt(start, goal, generator, max_time, max_iterations, max_generations, max_cost, max_length, debug,
         distance, sample, goal_sample, goal_probability):
  return search(pop_rrt(distance, sample, goal_sample, goal_probability), start, goal, generator,
                max_time, max_iterations, max_generations, max_cost, max_length, debug)
