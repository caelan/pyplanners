from ..operators import *

class Pick(Action):
  def __init__(self, obj):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    self.conditions = {
      ('clear', obj): True,
      ('on', obj): 'table',
      'holding': False
    }
    self.effects = {
      'holding': obj,
      ('clear', obj): False,
      ('on', obj): False,
    }

class Place(Action):
  def __init__(self, obj):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    self.conditions = {
      'holding': obj
    }
    self.effects = {
      'holding': False,
      ('clear', obj): True,
      ('on', obj): 'table',
    }

class Stack(Action):
  def __init__(self, obj, under_obj):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    self.conditions = {
      ('clear', under_obj): True,
      'holding': obj
    }
    self.effects = {
      'holding': False,
      ('clear', obj): True,
      ('on', obj): under_obj,
      ('clear', under_obj): False,
    }

class Unstack(Action):
  def __init__(self, obj, under_obj):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    self.conditions = {
      ('clear', obj): True,
      ('on', obj): under_obj,
      'holding': False
    }
    self.effects = {
      'holding': obj,
      ('clear', obj): False,
      ('on', obj): False,
      ('clear', under_obj): True,
    }

def line_stack_blocks(n=10, height=5):
#def line_stack_blocks(n=6, height=3):
  height = max(height, 0)
  n = max(height, n)
  blocks = ['Block%d'%i for i in range(1, n+1)]

  operators = [Pick(item) for item in blocks] + \
    [Place(item) for item in blocks] + \
    [Unstack(*item) for item in permutations(blocks, 2)] + \
    [Stack(*item) for item in permutations(blocks, 2)]

  initial = State(merge_dicts(
      {('on', block): 'table' for block in blocks},
      {('clear', block): True for block in blocks}
  ))

  goal = Goal(merge_dicts(
      {('on', blocks[0]): 'table', 'holding': False},
      {('on', obj): under_obj for under_obj, obj in pairs(blocks[:height])}
  ))

  return initial, goal, operators

def unstack_blocks(n=6, height=3):
  height = max(height, 0)
  n = max(height, n)
  blocks = ['Block%d'%i for i in range(1, n+1)]

  operators = [Pick(item) for item in blocks] + \
    [Place(item) for item in blocks] + \
    [Unstack(*item) for item in permutations(blocks, 2)] + \
    [Stack(*item) for item in permutations(blocks, 2)]

  initial = State(merge_dicts(
      {('on', blocks[0]): 'table', ('clear', blocks[height-1]): True},
      {('on', obj): under_obj for under_obj, obj in pairs(blocks[:height])},
      {('on', block): 'table' for block in blocks[height:]},
      {('clear', block): True for block in blocks[height:]},
  ))

  goal = Goal(merge_dicts(
      {('on', blocks[0]): blocks[-1]},
  ))

  return initial, goal, operators

def restack_blocks(n=10, height=5):
  height = max(height, 0)
  n = max(height, n)
  blocks = ['Block%d'%i for i in range(1, n+1)]

  operators = [Pick(item) for item in blocks] + \
    [Place(item) for item in blocks] + \
    [Unstack(*item) for item in permutations(blocks, 2)] + \
    [Stack(*item) for item in permutations(blocks, 2)]

  initial = State(merge_dicts(
      {('on', blocks[height-1]): 'table', ('clear', blocks[0]): True},
      {('on', obj): under_obj for under_obj, obj in pairs(blocks[:height][::-1])},
      {('on', block): 'table' for block in blocks[height:]},
      {('clear', block): True for block in blocks[height:]}
  ))

  goal = Goal(merge_dicts(
      {('on', blocks[0]): 'table', 'holding': False},
      {('on', obj): under_obj for under_obj, obj in pairs(blocks[:height])}
  ))

  return initial, goal, operators
