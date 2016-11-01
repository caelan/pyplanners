from states import *
from misc.utils import *
from effects import ValueEffect
from conditions import SubstateCondition

class Operator(object):
  def __init__(self, args):
    self.args = args
    for k, v in args.iteritems():
      setattr(self, k, v)
    self.conditions = []
    self.effects = {}
  def __contains__(self, state):
    return all(state in precondition for precondition in self.conditions)
  def apply(self, state):
    return State(dict(list(state) + [(var, effect(state)) for var, effect in self.effects.items()]))
  def __call__(self, state):
    if state not in self: return None
    return self.apply(state)
  def __iter__(self):
    yield self
  def __len__(self):
    return 1
  def fixed_conditions(self):
    fc = {}
    for condition in self.conditions:
      if isinstance(condition, SubstateCondition):
        for var, value in condition.substate:
          if var in fc and fc[var] != value:
            raise RuntimeError('Condition has conflicting conditions')
          fc[var] = value
    return fc
  def fixed_effects(self):
    return {var : effect.value for var, effect in self.effects.iteritems() if isinstance(effect, ValueEffect)}
  def fixed_image(self):
    return merge_dicts(self.fixed_conditions(), self.fixed_effects())
  #def image(self):
  #  pass
  #def fixed_preimage(self):
  #  pass
  def __eq__(self, other):
    if type(self) != type(other): return False
    return self.args == other.args
  def __ne__(self, other):
    return not self == other
  def __hash__(self):
    return hash((self.__class__, frozenset(self.args.items())))
  def __str__(self):
    return self.__class__.__name__ + str_args(self.args)
  __repr__ = __str__

class Action(Operator): cost = 1
class Axiom(Operator): cost = 0
class Inference(Operator): cost = 0

def get_applied_predicates(state, axioms): # TODO - layer axioms
  applied_predicates = []
  for axiom in axioms:
    new_state = axiom(state)
    if new_state is not None:
      state = new_state
      applied_predicates.append(axiom)
  return applied_predicates

def derive_predicates(state, axioms): # TODO - layer axioms
  for axiom in axioms:
    new_state = axiom(state)
    if new_state is not None:
      state = new_state
  return state

###########################################################################

class MacroOperator(object):
  def __init__(self, *operators):
    self.operators = tuple(operators)
    self.cost = sum(operator.cost for operator in operators)
  def __contains__(self, state):
    return self(state) is not None
  def __call__(self, state):
    states = [state]
    for operator in self.operators:
      new_state = operator(states[-1])
      if new_state is None: return None
      states.append(new_state)
    return states
  def __iter__(self):
    return (operator for operator in self.operators)
  def __len__(self):
    return len(self.operators)
  def __eq__(self, other):
    if type(self) != type(other): return False
    return self.operators == other.operators
  def __ne__(self, other):
    return not self == other
  def __hash__(self):
    return hash((self.__class__, self.operators))
  def __str__(self):
    return self.__class__.__name__ + str_object(self.operators)
  __repr__ = __str__
