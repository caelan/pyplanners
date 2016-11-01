from misc.utils import *

# NOTE
# - single underscore indicates protected; double underscore indicates private
# - can treat var as an arbitrary object and make the value True/False
# - this does limit the possible variables created to a finite, specified set though
# - contains is automatically generated

# None => anything
# False => not present/off

HASH_DICT = '__hash_dict'

class Substate(DictPrintObject, Mapping):
  def __init__(self, values):
    HashObject.__init__(self)
    self.__dict__[HASH_DICT] = values
  def variables(self):
    return set(self.__dict__[HASH_DICT].keys())
  def includes(self, other):
    return all(var in self and self[var] == other[var] for var in other.variables()) # TODO - test if state
  def __getitem__(self, var):
    return self.get(var)
  def __iter__(self):
    return self.__dict__[HASH_DICT].iteritems()
  def __len__(self):
    return len(self.__dict__[HASH_DICT])
  def __str__(self):
    return 'SS' + str_args(self.__dict__[HASH_DICT])

class State(Substate):
  def __init__(self, values):
    super(self.__class__, self).__init__({var: value for var, value in values.items() if value is not False})
  def __getitem__(self, var):
    if var not in self.__dict__[HASH_DICT]: return False
    return self.__dict__[HASH_DICT][var]
  def substate(self, variables):
    return Substate({var: self[var] for var in variables})
  def __call__(self, variables):
    return self.substate(variables)

# NOTE - the condition order determines the order in which conditions are processed
class PartialState(SinglePrintObject):
  #__slots__ = ('conditions',)
  def __init__(self, conditions):
    HashObject.__init__(self)
    self.conditions = tuple(conditions)
  def __contains__(self, state):
    return all(state in condition for condition in self.conditions)
  def __iter__(self):
    for condition in self.conditions:
      yield condition
  def __len__(self):
    return len(self.conditions)
