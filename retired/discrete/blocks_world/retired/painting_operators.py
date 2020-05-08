import inspect

from planner.domains import *
from planner.subsets import *
from blocks_world import *

class SprayPaint(Action):
  name, cost = 'SprayPaint', 1
  def __init__(self, obj, sprayer, color):
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    Action.__init__(self, {arg: values[arg] for arg in args if arg not in ['self']})
    self.transitions = {
      ('color', obj): Transition(None, color),
    }
    self.subsets = {
      ('on', obj): Value('table'),
      ('clear', obj): Value(True),
      ('paints', sprayer): Value(color),
      'holding': Value(sprayer)
    }

class LoadBrush(Action):
  name, cost = 'LoadBrush', 1
  def __init__(self, brush, can, color):
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    Action.__init__(self, {arg: values[arg] for arg in args if arg not in ['self']})
    self.transitions = {
      ('paints', brush): Transition(None, color),
    }
    self.subsets = {
      ('clear', can): Value(True),
      ('paints', can): Value(color),
      'holding': Value(brush)
    }

class BrushPaint(Action):
  name, cost = 'BrushPaint', 1
  def __init__(self, obj, brush, color):
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    Action.__init__(self, {arg: values[arg] for arg in args if arg not in ['self']})
    self.transitions = {
      ('color', obj): Transition(None, color),
    }
    self.subsets = {
      ('on', obj): Value('table'),
      ('clear', obj): Value(True),
      ('paints', brush): Value(color),
      'holding': Value(brush)
    }

class WashBrush(Action):
  name, cost = 'WashBrush', 1
  def __init__(self, brush, bucket, color):
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    Action.__init__(self, {arg: values[arg] for arg in args if arg not in ['self']})
    self.transitions = {
      ('paints', brush): Transition(color, None),
    }
    self.subsets = {
      ('clear', bucket): Value(True),
      'holding': Value(brush)
    }

def initialize():
  # Start State
  blocks = ['A', 'B']
  colors = ['red', 'blue', 'green']
  sprayers = ['red_sprayer']
  brushes = ['brush']
  cans = ['blue_can']
  buckets = ['bucket']

  start = State({
    ('on', 'A'): 'table',
    ('clear', 'A'): False,
    ('color', 'A'): None,

    ('on', 'B'): 'A',
    ('clear', 'B'): True,
    ('color', 'B'): None,

    ('on', 'red_sprayer'): 'table',
    ('clear', 'red_sprayer'): True,
    ('paints', 'red_sprayer'): 'red',

    ('on', 'brush'): 'table',
    ('clear', 'brush'): True,
    ('paints', 'brush'): None,

    ('on', 'blue_can'): 'table',
    ('clear', 'blue_can'): True,
    ('paints', 'blue_can'): 'blue',

    ('on', 'bucket'): 'table',
    ('clear', 'bucket'): True,

    'holding': None
  })

  # Goal State
  goal = PartialState({
    ('on', 'A'): Value('B'),
    ('color', 'A'): Value('red'),
    ('on', 'B'): Value('table'),
    ('color', 'B'): Value('blue'),
    'holding': Value(None)
  })

  actions = [Pick(item) for item in blocks + sprayers + brushes + cans + buckets] + \
    [Place(item) for item in blocks + sprayers + brushes + cans + buckets] + \
    [Unstack(*item) for item in permutations(blocks + sprayers + brushes + cans + buckets, 2)] + \
    [Stack(*item) for item in permutations(blocks + sprayers + brushes + cans + buckets, 2)] + \
    [SprayPaint(*item) for item in product(blocks, sprayers, colors)] + \
    [LoadBrush(*item) for item in product(brushes, cans, colors)] + \
    [BrushPaint(*item) for item in product(blocks, brushes, colors)] + \
    [WashBrush(*item) for item in product(brushes, buckets, colors)]

  return start, goal, ConnectivityGraph(create_discrete_domains(actions))
