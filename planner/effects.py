from misc.utils import *

# NOTE
# - effects must be defined for all values of some set of variables
# - they can, however, throw exceptions if not enough variables are defined

# TODO - conditional effects

class Effect(ValuesPrintObject):
  def __init__(self):
    HashObject.__init__(self)
  def __call__(self, *args):
    raise NotImplementedError('Effect must implement __call__(self, substate)')

class ValueEffect(Effect):
  def __init__(self, value):
    super(self.__class__, self).__init__()
    self.value = value
  def __call__(self, *args):
    return self.value
  def __repr__(self):
    return 'VE' + str_object((self.value,))

class FunctionEffect(Effect): # TODO - do I really want this functionality
  def __init__(self, variables, function):
    super(self.__class__, self).__init__()
    self.variables = variables
    self.function = function
  def __call__(self, substate):
    if not all(var in substate for var in self.variables):
      raise Exception('substate does not have necessary variables defined')
    return self.function({var: substate[var] for var in self.variables})

class FalseEffect(Effect):
  def __call__(self, *args):
    return False
