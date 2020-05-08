from retired.discrete.operators import add_operator_transitions
from planner.operators import Action
from misc.utils import arg_info, currentframe

class Pick(Action):
  def __init__(self, obj):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    add_operator_transitions(self, {
      ('on', obj): ('table', False),
      ('clear', obj): (True, None),
      'holding': (False, obj),
    })

class Place(Action):
  def __init__(self, obj):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    add_operator_transitions(self, {
      ('on', obj): (None, 'table'),
      'holding': (obj, False),
    })

class Unstack(Action):
  def __init__(self, obj, base_obj):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    add_operator_transitions(self, {
      ('on', obj): (base_obj, False),
      ('clear', obj): (True, None),
      'holding': (False, obj),
      ('clear', base_obj): (None, True),
    })

class Stack(Action):
  def __init__(self, obj, base_obj):
    super(self.__class__, self).__init__(arg_info(currentframe()))
    add_operator_transitions(self, {
      ('on', obj): (None, base_obj),
      'holding': (obj, False),
      ('clear', base_obj): (True, False),
    })
