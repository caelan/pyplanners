from .utils import *
from misc.objects import str_object
from misc.functions import flatten

class Vertex(object):
  def __init__(self, substate, rg):
    self.substate = substate
    self.rg = rg
    #self.sources = set() # (source_vertex, edge): edge(source) = self
    #self.sinks = set() # (sink_vertex, edge): edge(self) = sink_vertex
    #self.connectors = set()
    self.sources = [] # (source_vertex, edge): edge(source) = self
    self.sinks = [] # (sink_vertex, edge): edge(self) = sink_vertex
    self.connectors = [] # The sets are causing issues
    self.reset()

  def reset(self):
    self.reachable = False
    self.active = False
    self.activations = 0
    self.initial = False
    self.active_dirty_bit = 0

  def incoming(self):
    return [edge for _, edge in self.sinks] #+ [edge for source_vertex, _ in self.sinks]

  def outgoing(self):
    return self.connectors #+ [sink_vertex for sink_vertex, edge in self.sinks]

  def connected(self, connector):
    return connector in self.connectors

  def is_active(self):
    return self.active_dirty_bit == self.rg.active_dirty_bit

  def connect(self, connector):
    # TODO - check that the vertex satisfies the connector
    if connector not in self.connectors: # TODO - do we even need to check that is in the set?
      #self.connectors.add(connector)
      #connector.vertices.add(self)
      self.connectors.append(connector)
      connector.vertices.append(self)

      if connector.active and not self.active:
        self.set_active()
      if self.reachable and not connector.reachable:
        connector.set_reachable()

  def set_reachable(self):
    if self.reachable: return
    self.reachable = True

    if PRUNE_INACTIVE and self.rg.greedy:
      self.set_inactive()
    #for connector in list(self.connectors): # NOTE - I use list because iterable size changes over iteration
    for connector in self.connectors:
      if not connector.reachable:
        connector.set_reachable()
    #for sink_vertex, edge in list(self.sinks):
    #  if not sink_vertex.reachable and edge.reachable:
    #    sink_vertex.set_active()

  def set_active(self):
    if self.active: return
    if self.rg.greedy and self.reachable: return # NOTE - recently added
    if self.initial: return # NOTE - never activate start vertices

    self.active = True
    self.activations += 1
    for source_vertex, edge in self.sources:
      #if source_vertex is not None:
      #  source_vertex.set_active()
      edge.set_active()

  def set_inactive(self, force=False): # NOTE - Susceptible to cycles
    if not self.active: return

    if force or not any(connector.active for connector in self.connectors):
      self.active = False
      for source_vertex, edge in self.sources:
        edge.set_inactive()
        #if source_vertex is not None:
        #  source_vertex.set_inactive()

  """
  def set_inactive(self):
    if not self.active: return

    self.active = False
    for source_vertex, edge in self.sources:
      edge.update_inactive()
      #if source_vertex is not None:
      #  source_vertex.update_inactive()

  def update_inactive(self): # TODO - this is really slow. Only search if not greedy and reached?
    if not self.active: return

    self.active = False # Temporarily set to inactive
    for connector in self.connectors:
      connector.update_inactive()
      if connector.active:
        self.active = True
        return
    #for sink_vertex, _ in self.sinks:
    #  sink_vertex.update_inactive()
    #  if sink_vertex.active:
    #    self.active = True
    #    return
    # Cannot find active parent node
    self.set_inactive()
  """

  def __str__(self):
    return 'V(' + str(self.substate) + ')'
  __repr__ = __str__
  def node_str(self):
    #if len(self.substate) == 0: # If this happens, there is a problem...
    #  return 'EmptySet'
    return '\n'.join([str_object(variable) + '=' + str_object(value) for variable, value in self.substate])
  def node_attr(self):
    return {
      'shape': 'circle',
      'fontcolor': 'black',
      'style': 'filled',
      'colorscheme': 'SVG',
      'color': 'green' if self.initial else 'yellow',
      'fontname': 'times' + (' italic' if not self.reachable else '') + (' bold' if not self.active else '')
    }
