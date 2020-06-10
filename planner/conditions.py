from misc.utils import *

# TODO - require that each condition include the variables it tests

class Condition(ValuesPrintObject):
  def __init__(self):
    HashObject.__init__(self)
  def applicable(self, substate):
    return all(var in substate for var in self.variables)
  @abc.abstractmethod
  def __contains__(self, substate):
    raise NotImplementedError('Condition must implement __contains__(self, substate)')

class SubstateCondition(Condition):
  def __init__(self, substate):
    super(self.__class__, self).__init__()
    self.substate = substate
    self.variables = frozenset(substate.variables())
  def __contains__(self, substate):
    return all(var in substate and substate[var] == value for var, value in self.substate)
  def __str__(self):
    return 'SC' + str_args(self.substate.__dict__['__hash_dict'])
  __repr__ = __str__

#class MultiSubstateCondition(Condition): # TODO - should I take union of variables
#  def __init__(self, substates):
#    super(self.__class__, self).__init__()
#    self.substates = frozenset(substates)
#  def __contains__(self, substate):
#    return any(all(var in substate and substate[var] == value for var, value in ss) for ss in self.substates)

class TestCondition(Condition):
  def __init__(self, variables, test):
    super(self.__class__, self).__init__()
    self.variables = frozenset(variables)
    self.test = test
  def __call__(self, substate):
    return all(var in substate for var in self.variables) \
           and self.test({var: substate[var] for var in self.variables})

class AllCondition(Condition):
  variables = frozenset()
  def __contains__(self, substate):
    return True

class EmptyCondition(Condition):
  variables = frozenset()
  def __contains__(self, substate):
    return False
