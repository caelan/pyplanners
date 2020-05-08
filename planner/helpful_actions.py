from planner.operators import *

# TODO - when faced with parallel operator sequences, choose the least costly

def applicable_operators(rg, edge_test=lambda e: True, parallel=False):
  operators = set()
  successor_states = {rg.initial_state()}
  for edge in set(e for connector in rg.start.connectors for e in connector.edges if edge_test(e)):
    if edge != rg.goal:
      new_state = edge.value(rg.start.substate)
      if new_state is not None and (parallel or new_state not in successor_states):
        successor_states.add(new_state)
        operators.add(edge.value)
  return operators

# TODO - Macro operators within planner/mode
# NOTE - doesn't take into account fact that some actions may achieve goals that have a lower level (i.e. moving indirectly)
def applicable_macro_operators(rg, edge_test=lambda e: True, parallel=False, greedy=True):
  sequences = set()
  successor_states = {rg.initial_state()}
  reached_key = (lambda v, s: (v, s)) if not greedy else (lambda v, s: v)
  reached = {reached_key(vertex, rg.start.substate) for vertex in rg.initial_vertices()}
  def recur(vertex, state, sequence): # TODO - traverse this in a BFS/cost effective manner
    for edge in set(e for connector in vertex.connectors for e in connector.edges if e == rg.goal or edge_test(e)):
      if edge != rg.goal:
        context_state = edge.value(state)
        if context_state is not None:
          for _, next_vertex in edge.mappings:
            if not in_add(reached_key(next_vertex, context_state), reached):
              recur(next_vertex, context_state, sequence + [edge.value])
          continue
      if len(sequence) != 0 and (parallel or state not in successor_states): # goal achiever or a context_state is not applicable
        successor_states.add(state)
        sequences.add(MacroOperator(*sequence))
  for vertex in rg.initial_vertices():
    recur(vertex, rg.initial_state(), [])
  return sequences

#######################################################################

def goal_edges(rg, regression_test=lambda *args:True):
  vertices, connectors, edges = set(), set(), set()
  def recur(vertex):
    for source_vertex, edge in vertex.sources:
      if regression_test(rg, source_vertex, edge, vertex):
        if source_vertex is not None and not in_add(source_vertex, vertices):
          recur(source_vertex)
        if not in_add(edge, edges):
          for connector in edge.connectors:
            if not in_add(connector, connectors):
              for new_vertex in connector.vertices:
                if not in_add(new_vertex, vertices):
                  recur(new_vertex)

  for connector in rg.goal.connectors:
    if not in_add(connector, connectors):
      for new_vertex in connector.vertices:
        if not in_add(new_vertex, vertices):
          recur(new_vertex)
  return edges

def cost_goal_edges(rg):
  def cost_test(rg, source_vertex, edge, sink_vertex):
    return rg.op(edge.cost, (source_vertex.cost if source_vertex is not None else 0)) + \
        (edge.value.cost if not rg.unit else 1) <= sink_vertex.cost # Equals should be sufficient
  return goal_edges(rg, regression_test=cost_test)

def level_goal_edges(rg):
  def level_test(rg, source_vertex, edge, sink_vertex):
    return max(edge.level, (source_vertex.level if source_vertex is not None else 0)) + 1 <= sink_vertex.level # Equals should be sufficient
  return goal_edges(rg, regression_test=level_test)

###########################################################################

def achievers_dag(rg, l_fn=lambda n: n.level):
  vertex_arcs = defaultdict(set)
  edge_arcs = defaultdict(set)
  processed = set()
  def recur(vertex):
    if vertex in processed: return
    processed.add(vertex)
    for source, edge in rg.all_vertex_achievers(vertex, l_fn):
      edge_arcs[edge].add(vertex)
      for c in edge.connectors:
        for v in rg.all_connector_achievers(c, l_fn):
          vertex_arcs[v].add(edge)
          recur(v)
  for c in rg.goal.connectors:
    for v in rg.all_connector_achievers(c, l_fn):
      vertex_arcs[v].add(rg.goal)
      recur(v)
  return vertex_arcs, edge_arcs

# NOTE - the difference between this and applicable_macro_operators is the filtering of operators
def achieving_macro_operators(rg, parallel=False, greedy=True):
  vertex_arcs, edge_arcs = achievers_dag(rg)
  sequences = set()
  successor_states = {rg.initial_state()}
  reached_key = (lambda v, s: (v, s)) if not greedy else (lambda v, s: v)
  reached = {reached_key(vertex, rg.start.substate) for vertex in rg.initial_vertices()}
  def recur(vertex, state, sequence): # TODO - traverse this in a BFS/cost effective manner
    for edge in vertex_arcs[vertex]:
      if edge != rg.goal:
        context_state = edge.value(state)
        if context_state is not None:
          for next_vertex in edge_arcs[edge]:
            if not in_add(reached_key(next_vertex, context_state), reached):
              recur(next_vertex, context_state, sequence + [edge.value])
          continue
      if len(sequence) != 0 and (parallel or state not in successor_states): # goal achiever or a context_state is not applicable
        successor_states.add(state)
        sequences.add(MacroOperator(*sequence))
  for vertex in rg.initial_vertices():
    recur(vertex, rg.initial_state(), [])
  #operator_arcs = {edge.value: [next_edge for vert in arcs for next_edge in vertex_arcs[vert]] for edge, arcs in edge_arcs.items()}
  #for sequence in sequences:
  #  print(sequence, operator_arcs[sequence.operators[-1]])
  #print
  return sequences

###########################################################################

def macro(operators): return [MacroOperator(operator) for operator in operators]

def edge_test_fn(goal_vertices=None, goal_connectors=None, goal_edges=None):
  def edge_test(edge):
    if not (goal_edges is None or edge in goal_edges): return False
    if not (goal_vertices is None or any(v in goal_vertices for _, v in edge.mappings)): return False
    if not (goal_connectors is None or any(any(c in goal_connectors for c in v.connectors) for _, v in edge.mappings)): return False
    return True
  return edge_test

def filter_short(macro_ops, k=2):
  filtered = list(filter(lambda mo: len(mo) >= k, macro_ops))
  if len(filtered) == 0:
    return macro_ops
  return filtered

###########################################################################

# Reachability Graph
def ha_applicable(rg): return macro(applicable_operators(rg))
def ha_goal(rg): return macro(applicable_operators(rg, edge_test_fn(goal_edges=goal_edges(rg))))
def ha_cost_goal(rg): return macro(applicable_operators(rg, edge_test_fn(goal_edges=cost_goal_edges(rg))))
def ha_level_goal(rg): return macro(applicable_operators(rg, edge_test_fn(goal_edges=level_goal_edges(rg))))

def ha_applicable_macro(rg): return applicable_macro_operators(rg)
def ha_goal_macro(rg): return applicable_macro_operators(rg, edge_test_fn(goal_edges=goal_edges(rg)))
def ha_cost_goal_macro(rg): return applicable_macro_operators(rg, edge_test_fn(goal_edges=cost_goal_edges(rg)))
def ha_level_goal_macro(rg): return applicable_macro_operators(rg, edge_test_fn(goal_edges=level_goal_edges(rg)))

def ha_goal_macro_sorted(rg):
  return sorted(applicable_macro_operators(rg, edge_test_fn(goal_edges=goal_edges(rg))), key=lambda mo: len(mo), reverse=True)

def ha_level_goal_macro_sorted(rg):
  return sorted(applicable_macro_operators(rg, edge_test_fn(goal_edges=level_goal_edges(rg))), key=lambda mo: len(mo), reverse=True)

def ha_achieving_macro_sorted(rg):
  return filter_short(sorted(achieving_macro_operators(rg), key=lambda mo: len(mo), reverse=True))
  #return sorted(achieving_macro_operators(rg), key=lambda mo: len(mo), reverse=True)

###########################################################################

# Relaxed PlanGraph
def ha_relaxed_plan_goal(rg): return macro(applicable_operators(rg, edge_test_fn(goal_vertices=rg.relaxed_plan_vertices[1])))
def ha_relaxed_plan_action(rg): return macro(applicable_operators(rg, edge_test_fn(goal_edges=rg.relaxed_plan_edges[0])))

def ha_relaxed_plan_goal_macro(rg): return applicable_macro_operators(rg, edge_test_fn(goal_vertices=set(flatten(rg.relaxed_plan_vertices))))
def ha_relaxed_plan_action_macro(rg): return applicable_macro_operators(rg, edge_test_fn(goal_edges=set(flatten(rg.relaxed_plan_edges))))

def ha_relaxed_plan_goal_macro_sorted(rg):
  return sorted(applicable_macro_operators(rg, edge_test_fn(goal_vertices=set(flatten(rg.relaxed_plan_vertices)))),
                key=lambda mo: len(mo), reverse=True)
def ha_relaxed_plan_action_macro_sorted(rg):
  return sorted(applicable_macro_operators(rg, edge_test_fn(goal_edges=set(flatten(rg.relaxed_plan_edges)))),
                key=lambda mo: len(mo), reverse=True)
