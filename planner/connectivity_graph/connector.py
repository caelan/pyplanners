from utils import *
from misc.objects import str_object
from collections import defaultdict
from planner.states import Substate
from vertex import Vertex

class Connector(object):
  def __init__(self, condition, rg):
    self.condition = condition
    self.rg = rg
    #self.vertices = set()
    #self.edges = set()
    self.vertices = []
    self.edges = []
    self.subplanners = defaultdict(lambda: None)
    self.reset()

  def reset(self):
    self.reachable = False
    self.active = False
    self.activations = 0
    self.active_dirty_bit = 0

  def satisfies(self, vertex):
    return vertex.substate in self.condition

  def incoming(self):
    return self.vertices

  def outgoing(self):
    return self.edges

  def connected(self, edge):
    return edge in self.edges

  def is_active(self):
    return self.active_dirty_bit == self.rg.active_dirty_bit

  def connect(self, edge):
    # TODO - check that the connector belongs to the edge
    if edge not in self.edges: # This actually won't matter
      #self.edges.add(edge)
      self.edges.append(edge)
      edge.connectors.append(self)

      if edge.active and not self.active:
        edge.set_active_next_connector() # self.set_active() # TODO - why did I do this?
      if self.reachable and not edge.reachable:
        edge.num_reachable += 1
        if edge.num_reachable == len(edge.value.conditions):
          edge.set_reachable()
        elif DELAYED_ACTIVATION:
          edge.set_active_next_connector()

  def set_reachable(self):
    if self.reachable: return
    self.reachable = True

    if PRUNE_INACTIVE and self.rg.greedy:
      self.set_inactive()
    #for edge in list(self.edges):
    for edge in self.edges:
      if not edge.reachable:
        edge.num_reachable += 1
        if edge.num_reachable == len(edge.value.conditions):
          edge.set_reachable()
        elif DELAYED_ACTIVATION and edge.active: # NOTE - recently added
          edge.set_active_next_connector()

  def set_active(self):
    if self.active: return
    if self.rg.greedy and self.reachable: return # NOTE - recently added

    self.active = True
    self.activations += 1
    start = self.rg.start
    if start in self.condition:
      start_vertex = self.rg.vertex(Substate({var: self.rg.start[var] for var in self.condition.variables}))
      start_vertex.connect(self)
      #self.rg.start.connect(self)
      return

    if self.subplanners[start] is None:
      # TODO - decide to first generate only new subplanners or all
      # TODO - remove dependence of subplanners on Vertex start
      self.subplanners[start] = self.rg.scheduler(Vertex(start, self.rg), self) # Eventually will just take a connector (which is implicitly relative to the start)
      for subplanner in self.subplanners[start]:
        subplanner.creation = self.rg.state_uses[start]
        subplanner.generation_history = defaultdict(int)
    for subplanner in self.subplanners[start]:
      if not subplanner.exhausted and not subplanner.queued:
        if INITIAL_GENERATION:
          subplanner()
          if subplanner.exhausted: continue
        self.rg.queue.append(subplanner)
        subplanner.queued = True

    for vertex in self.vertices:
      vertex.set_active()
    #self.rg.queue += self.subplanners # TODO - Add before or after?

  def set_inactive(self, force=False): # NOTE - Susceptible to cycles
    if not self.active: return

    if force or not any(edge.active for edge in self.edges):
      self.active = False
      #if self.subplanners[self.rg.start] is not None: # NOTE - de-queue achieved things, this needs to happen immediately for this to work
      #  for subplanner in self.subplanners[self.rg.start]:
      #    subplanner.queued = False # Tells the planner to get rid of this
      for vertex in self.vertices:
        vertex.set_inactive()

  """
  def set_inactive(self):
    if not self.active: return

    self.active = False
    for vertex in self.vertices:
      vertex.update_inactive()

  def update_inactive(self): # TODO - this is really slow. Only search if not greedy and reached?
    if not self.active: return

    self.active = False # Temporarily set to inactive
    for edge in self.edges:
      edge.update_inactive()
      if edge.active:
        self.active = True
        return
    # Cannot find active parent node
    self.set_inactive()
  """

  #def copy(self, rg):
  #  new_connector = type(self)(self.condition, rg)
  #  pass

  def __str__(self):
    return 'C(' + str(self.condition) + ')'
  __repr__ = __str__
  def node_str(self):
    node_str = self.condition.__class__.__name__
    for value in self.condition.__dict__['__hash_dict'].values():
      node_str += '\n' + str_object(value)
    return node_str
  def node_attr(self):
    return {
      'shape': 'oval',
      'fontcolor': 'white',
      'style': 'filled',
      'colorscheme': 'SVG',
      'color': 'blue',
      'fontname': 'times' + (' italic' if not self.reachable else '') + (' bold' if not self.active else '')
    }
