from collections import deque

from .utils import pop_random, pop_rrt
from ..state_space import StateSpace
from misc.functions import elapsed_time

def simple_search(pop, start, goal, generator, max_time, max_iterations, max_generations, max_cost, max_length, debug):
  space = StateSpace(generator, start, 1, max_generations, max_cost, max_length)
  sv = space.root
  if sv.contained(goal):
    return space.solution(sv)
  queue = deque([sv])
  while queue and (elapsed_time(space.start_time) < max_time) and (space.iterations < max_iterations):
    cv = pop(queue)
    space.iterations += 1
    if debug is not None:
      debug(cv)

    while cv.generate(): # TODO: generate_all
      pass
    if cv.h_cost is None:
      break
    for nv in cv.unexplored(): # TODO - should reverse order for DFS
      if nv.contained(goal):
        return space.solution(nv)
      queue.append(nv)
  return space.failure()

##################################################

def dfs(*args):
  return simple_search(lambda queue: queue.pop(), *args)

def bfs(*args):
  return simple_search(lambda queue: queue.popleft(), *args)

def srandom_walk(*args):
  return simple_search(pop_random, *args)

def srrt(start, goal, generator, max_time, max_iterations, max_generations, max_cost, max_length, debug,
         distance, sample, goal_sample, goal_probability):
  return simple_search(pop_rrt(distance, sample, goal_sample, goal_probability), start, goal, generator,
                       max_time, max_iterations, max_generations, max_cost, max_length, debug)
