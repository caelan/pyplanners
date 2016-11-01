from utils import *
from planner.operators import Operator
from misc.utils import str_object

class Edge(object):
  def __init__(self, value, rg):
    self.value = value
    self.rg = rg
    self.connectors = []
    self.intermediates = set()
    #self.mappings = set() # (source_vertex, sink_vertex)
    self.mappings = [] # (source_vertex, sink_vertex)
    self.reset()

  def reset(self):
    self.reachable = False
    self.num_reachable = 0
    self.active = False
    self.activations = 0
    self.active_dirty_bit = 0

  def incoming(self):
    return self.connectors

  def outgoing(self):
    return [sink_vertex for _, sink_vertex in self.mappings]

  def connected(self, sink_vertex, source_vertex=None):
    return (source_vertex, sink_vertex) in self.mappings

  def is_active(self):
    return self.active_dirty_bit == self.rg.active_dirty_bit

  def connect(self, sink_vertex, source_vertex=None):
    # TODO - check that the source vertex could satisfy the preconditions and the effect is correct
    if (source_vertex, sink_vertex) not in self.mappings:
      #sink_vertex.sources.add((source_vertex, self))
      #self.mappings.add((source_vertex, sink_vertex))
      #if source_vertex is not None: source_vertex.sinks.add((sink_vertex, self))
      sink_vertex.sources.append((source_vertex, self))
      self.mappings.append((source_vertex, sink_vertex))
      if source_vertex is not None: source_vertex.sinks.append((sink_vertex, self))

      if sink_vertex.active and not self.active:
        self.set_active()
      if sink_vertex.active and source_vertex is not None and not source_vertex.active:
        source_vertex.set_active()
      if (self.reachable and (source_vertex is None or source_vertex.reachable)) and not sink_vertex.reachable:
        sink_vertex.set_reachable()

  def set_reachable(self):
    if self.reachable: return
    self.reachable = True

    if PRUNE_INACTIVE and self.rg.greedy:
      self.set_inactive()
    #for source_vertex, sink_vertex in list(self.mappings):
    for source_vertex, sink_vertex in self.mappings:
      if not sink_vertex.reachable and (source_vertex is None or source_vertex.reachable):
        sink_vertex.set_reachable()

  def set_active(self):
    if self.active: return
    if self.rg.greedy and self.reachable: return # NOTE - recently added
    self.active = True
    self.activations += 1
    self.set_active_next_connector()

  def set_active_next_connector(self):
    if not self.active: return # NOTE - recently added
    if INTERMEDIATES_FIRST:
      #if not all(intermediate.reachable for intermediate in self.intermediates): return # NOTE - doesn't active edges achieving intermediates
      for connector in self.intermediates:
        if not self.rg.greedy or not connector.reachable:
          for vertex in connector.vertices:
            vertex.set_active() # NOTE - weird because skips the connector
        if DELAYED_ACTIVATION and not connector.reachable:
          return
      for connector in self.connectors:
        if connector in self.intermediates: continue
        if not self.rg.greedy or not connector.reachable:
          connector.set_active()
        if DELAYED_ACTIVATION and not connector.reachable:
          return
    else:
      #if REACHABLE_EXPAND and self.num_reachable < len(self.connectors):
      #  self.connectors[self.num_reachable].set_active() # TODO - fix this
      #else:
      #  for connector in self.connectors:
      #    if not self.rg.greedy or not connector.reachable:
      #      connector.set_active()
      for connector in self.connectors:
        if not self.rg.greedy or not connector.reachable:
          connector.set_active()
        if DELAYED_ACTIVATION and not connector.reachable:
          return

  def set_inactive(self, force=False): # NOTE - Susceptible to cycles
    if not self.active: return

    if force or not any(sink_vertex.active for _, sink_vertex in self.mappings):
      self.active = False
      for connector in self.connectors:
        connector.set_inactive()
      #for source_vertex, _ in self.mappings:
      #  if source_vertex is not None:
      #    source_vertex.set_inactive()

  """
  def set_inactive(self):
    if not self.active: return

    self.active = False
    for connector in self.connectors:
      connector.update_inactive()
    #for source_vertex, _ in self.mappings:
    #  if source_vertex is not None:
    #    source_vertex.update_inactive()

  def update_inactive(self):
    if not self.active or self == self.rg.goal: return # TODO - decide if better condition

    self.active = False # Temporarily set to inactive
    for _, sink_vertex in self.mappings:
      sink_vertex.update_inactive()
      if sink_vertex.active:
        self.active = True
        return
    # Cannot find active parent node
    self.set_inactive()
  """

  def __str__(self):
    return 'E(' + str(self.value) + ')'
  __repr__ = __str__
  def node_str(self):
    node_str = self.value.__class__.__name__
    if isinstance(self.value, Operator):
      for name, arg in self.value.args.items():
        node_str += '\n' + str_object(name) + '=' + str_object(arg)
    return node_str
  def node_attr(self):
    return {
      'shape': 'square',
      'fontcolor': 'white',
      'style': 'filled',
      'colorscheme': 'SVG',
      'color': 'black' if isinstance(self.value, Operator) else 'red',
      'fontname': 'times' + (' italic' if not self.reachable else '') + (' bold' if not self.active else '')
    }
