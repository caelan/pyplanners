from .utils import *
from ..state_space import *

def search(pop, start, goal, generator, recurrence, max_time, max_iterations, max_generations, max_cost, max_length, debug):
  state_space = StateSpace(generator, start, 1, max_generations, max_cost, max_length)
  sv = state_space.root
  if sv.contained(goal): return state_space.plan(sv), state_space
  if not sv.generate(): return None, state_space
  queue = deque([sv])
  sv.pops = 0
  while len(queue) > 0 and time() - state_space.start_time < max_time and state_space.iterations < max_iterations:
    cv = pop(queue); cv.pops += 1
    if (cv.pops - 1) % recurrence != 0: queue.append(cv); continue
    state_space.iterations += 1
    if debug is not None: debug(cv)

    for nv in cv.unexplored(): # TODO - should reverse order for DFS
      nv.pops = 0
      if nv.contained(goal):
        return state_space.plan(nv), state_space
      if nv.generate():
        queue.append(nv)
    if cv.generate():
      queue.append(cv)
  return None, state_space

def rdfs(*args):
  return search(lambda queue: queue.pop(), *args)

def rbfs(*args):
  return search(lambda queue: queue.popleft(),  *args)

def random_walk(*args):
  return search(pop_random, *args)

def rrt(start, goal, generator, recurrence, max_time, max_iterations, max_generations, max_cost, max_length, debug, distance, sample, goal_sample, goal_probability):
  return search(pop_rrt(distance, sample, goal_sample, goal_probability), start, goal, generator, recurrence, max_time, max_iterations, max_generations, max_cost, max_length, debug)
