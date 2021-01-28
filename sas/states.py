from misc.utils import *

# SAS+ := Simplified Action Structures (SAS) with possibility of having no requirement (+)
# TODO - extension that allows a discrete disjunction of values per variable

class State(object):
  def __init__(self, values):
    self.values = {var: value for var, value in values.items() if value is not False}
  def __getitem__(self, var):
    if var not in self.values: return False
    return self.values[var]
  def __eq__(self, other):
    return (type(self) == type(other)) and (self.values == other.values)
  def __ne__(self, other):
    return not self == other
  def __hash__(self):
    return hash((self.__class__, frozenset(self.values.items())))
  def __str__(self):
    return self.__class__.__name__ + str_object(self.values)
  __repr__ = __str__

class PartialState(object):
  def cond(self):
    return self.conditions.items()
  def __contains__(self, state):
    return all(state[var] == value for var, value in self.cond()) #and self.test(state)

class Goal(PartialState): # TODO: unify PartialState and Goal
  def __init__(self, values, test=lambda state: True):
    self.conditions = values
    self.test = test
  def __eq__(self, other):
    return (type(self) == type(other)) and (self.conditions == other.conditions)
  def __ne__(self, other):
    return not self == other
  def __hash__(self):
    return hash((self.__class__, frozenset(self.cond())))
  def __str__(self):
    return self.__class__.__name__ + str_object(self.conditions)
  __repr__ = __str__
