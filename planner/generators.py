from misc.utils import *

# TODO - include heuristics instead of vertex.h_cost

def operators_generator(vertex, operators):
  yield vertex.h_cost, operators

def succesors_generator(vertex, succesors):
  yield vertex.h_cost, succesors(vertex.state)

def infinite_succesors_generator(vertex, succesors):
  for operators in succesors(vertex.state):
    yield vertex.h_cost, operators

def independent_succesors_generator(vertex, succesors):
  while True:
    operators = succesors(vertex.state)
    if operators is None: return
    yield vertex.h_cost, operators

#################################################################

def reachability_generator(vertex, rg, h_fn, ha_fn, max_time=INF, max_iterations=INF, max_cycles=INF):
  while not rg.exhausted:
    rg.grow(max_time=max_time, max_iterations=max_iterations, max_cycles=max_cycles, greedy=True)
    if rg.reachable:
      yield h_fn(rg), ha_fn(rg)
    else:
      yield INF if not rg.exhausted else None, []

# TODO - distinguish between samples and generations?
# NOTE - still want to compute reachabilty each time even if not adding new samples
def connectivity_generator(vertex, cg, h_fn, ha_fn, max_time=INF, max_iterations=INF,
                           max_cycles=INF, max_generations=INF, greedy=True):
  reachable, exhausted = False, False
  while not exhausted:
    reachable, exhausted = cg.grow(vertex.state, max_time=max_time, max_iterations=max_iterations,
                                   max_cycles=max_cycles, max_generations=max_generations, greedy=greedy)
    if reachable:
      #h, ha = h_fn(cg), ha_fn(cg)
      #for a in ha:
      #  print(a)
      #yield h, ha
      yield h_fn(cg), ha_fn(cg)
    else:
      print('Not reachable')
      print(vertex.state)
      #for c, connector in cg.connectors.items():
      #  if connector.active and not connector.reachable:
      #    print(c, connector.edges)
      #for connector in cg.goal.connectors:
      #  print(connector, connector.reachable, connector.active)
      #raw_input()
      yield INF if not exhausted else None, []

# def restart_reachability_generator(...) # Restarts if too much time passes
