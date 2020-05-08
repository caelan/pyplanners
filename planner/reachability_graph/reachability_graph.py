from .vertex import Vertex
from .connector import Connector
from .edge import Edge
from .utils import graphviz_connect
from misc.objects import str_object
from planner.conditions import SubstateCondition
from planner.effects import ValueEffect
from planner.states import Substate

# NOTE
# - Don't have to worry about no preconditions but effects in this model
# - Can automatically propagate costs in a Bellman-Ford/Dijkstra manner while building the graph
# - Can use same scheduler for each reachability graph or make new one

# TODO
# - Grow until it reaches a specified h_cost. Note that you can avoid expanding nodes that aren't stopping the min-cost
# - Remember previously attempted actions
# - Axioms
# - Metric-FF

CONNECT_START = False
CONNECT_SUBSTATE = False
CONNECT_EFFECTS = False

class ReachabilityGraph(object): # TODO - Maybe just call ConnectivityGraph and generalize to other structures
  def __init__(self, start, goal, Scheduler):
    self.vertices = {}
    self.edges = {}
    self.connectors = {}

    self.reachable, self.exhausted = False, False
    self.total_time, self.total_iterations, self.total_cycles = 0, 0, 0
    self.start = self.vertex(start)
    self.goal = self.edge(goal)
    self.scheduler = Scheduler(self)

  def initial_state(self):
    return self.start.substate
  def initial_vertices(self):
    return [self.start]

  def vertex(self, substate):
    if substate not in self.vertices:
      self.vertices[substate] = Vertex(substate, self)
    return self.vertices[substate]
  def connector(self, condition):
    if condition not in self.connectors:
      self.connectors[condition] = Connector(condition, self)
      if CONNECT_SUBSTATE and isinstance(condition, SubstateCondition):
        self.vertex(condition.substate).connect(self.connectors[condition])
      if CONNECT_START and self.start.substate in condition:
        self.start.connect(self.connectors[condition])
    return self.connectors[condition]
  def edge(self, value): # intermediates=set()
    if value not in self.edges:
      edge = Edge(value, self)
      self.edges[value] = edge
      for condition in value.conditions:
        self.connector(condition).connect(edge)
      if CONNECT_EFFECTS and hasattr(value, 'effects'):
        for variable, effect in value.effects.items():
          if isinstance(effect, ValueEffect):
            edge.connect(self.vertex(Substate({variable: effect.value})))
    return self.edges[value]

  def grow(self):
    raise NotImplementedError('ReachabilityGraph must implement grow(self)')

  def graph(self, filename, reachable=True):
    from pygraphviz import AGraph # NOTE - LIS machines do not have pygraphviz
    graph = AGraph(strict=True, directed=True)

    for vertex in self.vertices.values():
      for connector in vertex.connectors:
        if not reachable or (vertex.reachable and connector.reachable):
          graphviz_connect(graph, vertex, connector)
    for connector in self.connectors.values():
      for edge in connector.edges:
        if not reachable or (connector.reachable and edge.reachable):
          graphviz_connect(graph, connector, edge)
    for edge in self.edges.values():
      for _, sink_vertex in edge.mappings:
        if not reachable or (edge.reachable and sink_vertex.reachable):
          graphviz_connect(graph, edge, sink_vertex)

    graph.draw(filename, prog='dot')

  # Can open each subplanner and close if content with the existing connections in the graph
  def copy(self, new_start, Scheduler):
    new_rg = self.__class__(new_start, self.goal, Scheduler)

  #def __copy__(self):
  #  pass
  #def __deepcopy__(self):
  #  pass

  def __repr__(self):
    return self.__class__.__name__ + \
        '\n\nVertices: ' + str_object(self.vertices.values()) + \
        '\n\nConnectors: ' + str_object(self.connectors.values()) + \
        '\n\nEdges: ' + str_object(self.edges.values())
