from misc.numerical import INF
from retired.planners.connectivity_graph.relaxed_connectivity_graph import RelaxedConnectivityGraph
#from .reachability_graph.relaxed_plan_graph import RelaxedPlanGraph
from planner.generators import connectivity_generator
from planner.helpful_actions import ha_achieving_macro_sorted
from planner.heuristics import h_ff_add

"""
def redo_scheduler_generator(goal, Scheduler):
  reachability_graph = RelaxedPlanGraph
  heuristic = h_ff_add
  helpful_actions = ha_relaxed_plan_action_macro_sorted
  max_time = INF
  max_iterations = INF
  max_cycles = INF
  return lambda vertex: reachability_generator(vertex, reachability_graph(vertex.state, goal, Scheduler),
      heuristic, helpful_actions, max_time=max_time, max_iterations=max_iterations, max_cycles=max_cycles) # TODO - clean up scheduler
    #special_reachability_generator(vertex, reachability_graph(vertex.state, goal, Scheduler), heuristic, helpful_actions)
"""

#def reuse_scheduler_generator(goal, Scheduler):
def default_scheduler_generator(goal, Scheduler):
  connectivity_graph = RelaxedConnectivityGraph(goal, Scheduler)
  heuristic = h_ff_add
  helpful_actions = ha_achieving_macro_sorted # ha_relaxed_plan_action_macro_sorted | ha_achieving_macro_sorted
  max_time = INF
  max_iterations = INF
  max_cycles = INF
  max_generations = INF
  greedy = False
  return lambda vertex: connectivity_generator(vertex, connectivity_graph, heuristic, helpful_actions,
      max_time=max_time, max_iterations=max_iterations, max_cycles=max_cycles, max_generations=max_generations, greedy=greedy)