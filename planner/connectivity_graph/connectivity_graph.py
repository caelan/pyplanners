from vertex import Vertex
from connector import Connector
from edge import Edge
from utils import graphviz_connect
from misc.objects import str_object
from planner.conditions import SubstateCondition
from planner.effects import ValueEffect
from planner.states import Substate
from collections import deque, defaultdict

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

class ConnectivityGraph(object): # TODO - Maybe just call ConnectivityGraph and generalize to other structures
  def __init__(self, goal, Scheduler):
    self.vertices = {}
    self.edges = {}
    self.connectors = {}

    self.total_time, self.total_iterations, self.total_cycles = 0, 0, 0
    self.start = None
    self.goal = self.edge(goal)
    self.scheduler = Scheduler(self)
    self.state_uses = defaultdict(int)
    self.active_dirty_bit = 0
    self.dirty_bit = False # TODO - mark if the connectivity graph changed at all

  def initial_state(self):
    return self.start
  def initial_vertices(self):
    return [vertex for vertex in self.vertices.values() if vertex.initial]

  def vertex(self, substate):
    if substate not in self.vertices:
      vertex = Vertex(substate, self)
      self.vertices[substate] = vertex
      if self.start.includes(vertex.substate):
        vertex.initial = True
        vertex.set_reachable()
    return self.vertices[substate]
  def connector(self, condition):
    if condition not in self.connectors:
      self.connectors[condition] = Connector(condition, self)
      #if CONNECT_SUBSTATE and isinstance(condition, SubstateCondition):
      #  self.vertex(condition.substate).connect(self.connectors[condition])
      #if CONNECT_START and self.start.substate in condition:
      #  self.start.connect(self.connectors[condition])
    return self.connectors[condition]
  def edge(self, value): # intermediates=set()
    if value not in self.edges:
      edge = Edge(value, self)
      self.edges[value] = edge
      for condition in value.conditions: # NOTE - might want
        self.connector(condition).connect(edge)
      #if CONNECT_EFFECTS and hasattr(value, 'effects'):
      #  for variable, effect in value.effects.iteritems():
      #    if isinstance(effect, ValueEffect):
      #      edge.connect(self.vertex(Substate({variable: effect.value})))
    return self.edges[value]

  def get_achievers(self, goal_connector):
    return [edge.value for vertex in goal_connector.vertices for _, edge in vertex.sources] # TODO - source vertex
  def add_achiever(self, action, goal_connector):
    assert all(isinstance(eff, ValueEffect) for eff in action.effects.values())
    effect_vertex = self.vertex(Substate({var: value for var, value in action.fixed_image().iteritems()
                                        if var in goal_connector.condition.variables})) # TODO - conditional effects
    #if action in self.edges: return False # Returns false for existing actions
    if goal_connector.satisfies(effect_vertex):
      edge = self.edge(action)
      if effect_vertex.connected(goal_connector) and edge.connected(effect_vertex, source_vertex=None):
        return False
      effect_vertex.connect(goal_connector)
      edge.connect(effect_vertex)
    else:
      print action, goal_connector
      raise RuntimeError('Action does not achieve goal') # TODO - remove
    return True

  # TODO - for failed branches in the DFS (that don't self intersect) can declare done
  def is_connector_active(self, connector):
    if not connector.active: return False
    nodes = {connector}
    stack = deque([connector])
    while len(stack) != 0:
      node1 = stack.pop()
      for node2 in node1.outgoing():
        if node2.active and not node2 in nodes:
          if node2 == self.goal:
            return True
          stack.append(node2)
          nodes.add(node2)
    for node in nodes:
      node.set_inactive(force=True) # TODO - maybe do these all at once?
      #node.active = False
    return False

  # TODO - instead do the dirty bit which updates reachability from the goal lazily when something changed
  def update_active(self, node1=None):
    if node1 == None:
      node1 = self.goal
      self.active_dirty_bit += 1
    if node1.reachable or node1.active_dirty_bit == self.active_dirty_bit: return # NOTE - only continue if something is already active
    node1.active_dirty_bit = self.active_dirty_bit

    for node2 in node1.incoming():
      self.update_active(node2)

  def grow(self, start):
    raise NotImplementedError(self.__class__.__name__ + ' must implement grow(self, start)')

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

  def __repr__(self):
    return self.__class__.__name__ + \
        '\n\nVertices: ' + str_object(self.vertices.values()) + \
        '\n\nConnectors: ' + str_object(self.connectors.values()) + \
        '\n\nEdges: ' + str_object(self.edges.values())
