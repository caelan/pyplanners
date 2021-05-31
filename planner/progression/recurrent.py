from collections import deque

from .utils import pop_random, pop_rrt
from ..state_space import StateSpace
from misc.functions import elapsed_time

def recurrent_search(pop, start, goal, generator, recurrence, max_time, max_iterations, max_generations, max_cost, max_length, debug):
  space = StateSpace(generator, start, 1, max_generations, max_cost, max_length)
  sv = space.root
  if sv.contained(goal):
    return space.solution(sv)
  if not sv.generate():
    return space.failure()
  queue = deque([sv])
  sv.pops = 0
  while queue and (elapsed_time(space.start_time) < max_time) and (space.iterations < max_iterations):
    cv = pop(queue)
    cv.pops += 1
    if (cv.pops - 1) % recurrence != 0:
      queue.append(cv)
      continue
    space.iterations += 1
    if debug is not None:
      debug(cv)

    for nv in cv.unexplored(): # TODO - should reverse order for DFS
      nv.pops = 0
      if nv.contained(goal):
        return space.solution(nv)
      if nv.generate():
        queue.append(nv)
    if cv.generate():
      queue.append(cv)
  return space.failure()

##################################################

def rdfs(*args):
  return recurrent_search(lambda queue: queue.pop(), *args)

def rbfs(*args):
  return recurrent_search(lambda queue: queue.popleft(), *args)

def random_walk(*args):
  return recurrent_search(pop_random, *args)

def rrt(start, goal, generator, recurrence, max_time, max_iterations, max_generations, max_cost, max_length,
        debug, distance, sample, goal_sample, goal_probability):
  return recurrent_search(pop_rrt(distance, sample, goal_sample, goal_probability), start, goal, generator, recurrence,
                          max_time, max_iterations, max_generations, max_cost, max_length, debug)
