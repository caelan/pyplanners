from utils import *
from misc.objects import str_object

class Connector(object):
  def __init__(self, condition, rg):
    self.condition = condition
    self.rg = rg
    self.vertices = set()
    self.edges = set()
    self.subplanners = None
    self.reachable = False
    self.active = False

  def satisfies(self, vertex):
    return vertex.substate in self.condition

  def connect(self, edge):
    # TODO - check that the connector belongs to the edge
    if edge not in self.edges: # This actually won't matter
      self.edges.add(edge)
      edge.connectors.append(self)

      if edge.active and not self.active:
        edge.set_active_next_connector() # self.set_active()
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
    for edge in list(self.edges):
      if not edge.reachable:
        edge.num_reachable += 1
        if edge.num_reachable == len(edge.value.conditions):
          edge.set_reachable()
        elif DELAYED_ACTIVATION:
          edge.set_active_next_connector()

  def set_active(self):
    if self.active: return
    self.active = True

    if self.rg.start.substate in self.condition:
      self.rg.start.connect(self)
      return
    if self.subplanners is None:
      # TODO - decide to first generate only new subplanners or all
      self.subplanners = self.rg.scheduler(self.rg.start, self) # Eventually will just take a connector (which is implicitly relative to the start)
    for subplanner in self.subplanners:
      if not subplanner.exhausted and not subplanner.queued:
        if INITIAL_GENERATION:
          subplanner()
          if subplanner.exhausted: continue
        self.rg.queue.append(subplanner)
        subplanner.queued = True
    for vertex in self.vertices:
      vertex.set_active()
    #self.rg.queue += self.subplanners # TODO - Add before or after?

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
      'fontname': 'times' + (' italic' if not self.reachable else '')
    }
