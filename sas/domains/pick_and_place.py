from ..operators import *

class Pick(Action):
  def __init__(self, obj, p):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    self.conditions = {
      ('clear', obj): True,
      ('on', obj): 'table',
      'holding': False,
      obj: p,
      'robot': p,
    }
    self.effects = {
      'holding': obj,
      ('clear', obj): False,
      ('on', obj): False,
      obj: False,
    }

class Place(Action):
  def __init__(self, obj, p):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    self.conditions = {
      'holding': obj,
      #obj: False,
      'robot': p,
    }
    self.effects = {
      'holding': False,
      ('clear', obj): True,
      ('on', obj): 'table',
      obj: p,
    }

class Unstack(Action):
  def __init__(self, obj, under_obj, p):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    self.conditions = {
      ('clear', obj): True,
      ('on', obj): under_obj,
      'holding': False,
      #under_obj: p,
      obj: p,
      'robot': p,
    }
    self.effects = {
      'holding': obj,
      ('clear', obj): False,
      ('on', obj): False,
      ('clear', under_obj): True,
      obj: False,
    }

class Stack(Action):
  def __init__(self, obj, under_obj, p):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    self.conditions = {
      ('clear', under_obj): True,
      'holding': obj,
      under_obj: p,
      #obj: False,
      'robot': p,
    }
    self.effects = {
      'holding': False,
      ('clear', obj): True,
      ('on', obj): under_obj,
      ('clear', under_obj): False,
      obj: p,
    }

class Move(Action):
  def __init__(self, p1, p2):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    self.conditions = {
      'robot': p1,
    }
    self.effects = {
      'robot': p2,
    }

def pp_line_stack_blocks(n=4, height=3, num_locations=4):
  assert height <= n
  assert num_locations >= n
  blocks = ['Block%d'%i for i in range(1, n+1)]
  locations = range(num_locations) + [None]

  operators = [Pick(item, loc) for item in blocks for loc in locations] + \
    [Place(item, loc) for item in blocks for loc in locations] + \
    [Unstack(item1, item2, loc) for item1, item2 in permutations(blocks, 2) for loc in locations] + \
    [Stack(item1, item2, loc) for item1, item2 in permutations(blocks, 2) for loc in locations] + \
    [Move(loc1, loc2) for loc1, loc2 in permutations(locations, 2)]

  initial = State(merge_dicts(
      {'robot': None},
      {block: locations[i] for i, block in enumerate(blocks)},
      {('on', block): 'table' for block in blocks},
      {('clear', block): True for block in blocks}
  ))

  goal = Goal(merge_dicts(
      #{('on', blocks[0]): 'table', 'holding': False},
      {('on', blocks[0]): 'table', 'holding': False, 'robot': None},
      {('on', obj): under_obj for under_obj, obj in pairs(blocks[:height])}
  ))

  return initial, goal, operators
