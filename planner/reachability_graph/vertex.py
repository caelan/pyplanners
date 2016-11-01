from utils import *
from planner.states import State
from misc.objects import str_object

class Vertex(object):
  def __init__(self, substate, rg):
    self.substate = substate
    self.rg = rg
    self.sources = set() # (source_vertex, edge)
    self.sinks = set() # (sink_vertex, edge)
    self.connectors = set()
    self.reachable = False
    self.active = False

  def connect(self, connector):
    # TODO - check that the vertex satisfies the connector
    if connector not in self.connectors:
      self.connectors.add(connector)
      connector.vertices.add(self)

      if connector.active and not self.active:
        self.set_active()
      if self.reachable and not connector.reachable:
        connector.set_reachable()

  def set_reachable(self):
    if self.reachable: return
    self.reachable = True

    # list is needed because iterable size changes over iteration
    if PRUNE_INACTIVE and self.rg.greedy:
      self.set_inactive()
    for connector in list(self.connectors):
      if not connector.reachable:
        connector.set_reachable()
    for sink_vertex, edge in list(self.sinks):
      if not sink_vertex.reachable and edge.reachable:
        sink_vertex.set_active()

  def set_active(self):
    if self.active: return
    self.active = True

    for source_vertex, edge in self.sources:
      if source_vertex is not None:
        source_vertex.set_active()
      edge.set_active()

  def set_inactive(self):
    if not self.active: return

    self.active = False
    for source_vertex, edge in self.sources:
      edge.update_inactive()
      if source_vertex is not None:
        source_vertex.update_inactive()

  def update_inactive(self): # TODO - this is really slow. Only search if not greedy and reached?
    if not self.active: return

    self.active = False # Temporarily set to inactive
    for connector in self.connectors:
      connector.update_inactive()
      if connector.active:
        self.active = True
        return
    for sink_vertex, _ in self.sinks:
      sink_vertex.update_inactive()
      if sink_vertex.active:
        self.active = True
        return
    # Cannot find active parent node
    self.set_inactive()

  def __str__(self):
    return 'V(' + str(self.substate) + ')'
  __repr__ = __str__
  def node_str(self):
    if isinstance(self.substate, State):
      return self.substate.__class__.__name__
    return '\n'.join([str_object(variable) + '=' + str_object(value) for variable, value in self.substate])
  def node_attr(self):
    return {
      'shape': 'circle',
      'fontcolor': 'black',
      'style': 'filled',
      'colorscheme': 'SVG',
      'color': 'green' if isinstance(self.substate, State) else 'yellow',
      'fontname': 'times' + (' italic' if not self.reachable else '')
    }
