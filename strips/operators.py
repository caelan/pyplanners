from states import *

class Operator(object):
  def __init__(self, args):
    for k, v in args.iteritems(): setattr(self, k, v)
    self.args = args # TODO - use FrozenDict instead
    self._frozen_args = frozenset(args.items())
    self._hash = None
  def __contains__(self, state):
    return all(literal in state for literal in self.conditions)
  def apply(self, state):
    return State({atom for atom in state.atoms if ~atom not in self.effects} |
        {literal for literal in self.effects if literal.sign})
  def is_axiom(self):
    return isinstance(self, Axiom)
  def __call__(self, state):
    if state not in self: return None
    return self.apply(state)
  def __iter__(self):
    yield self
  def __len__(self):
    return 1
  def __eq__(self, other):
    return type(self) == type(other) and self._frozen_args == other._frozen_args
  def __ne__(self, other):
    return not self == other
  def __hash__(self):
    if self._hash is None: self._hash = hash((self.__class__, self._frozen_args))
    return self._hash
  def __str__(self):
    return self.__class__.__name__ + str_object(self.args)
  __repr__ = __str__

class Action(Operator): cost = 1
class Axiom(Operator): cost = 0
class Inference(Operator): cost = 0
