from states import *

class Operator(PartialState):
  def __init__(self, args):
    for k, v in args.items():
        setattr(self, k, v)
    self.args = args # TODO - use FrozenDict instead
    self._frozen_args = frozenset(args.items())
    self._hash = None
  def eff(self):
    return self.effects.items()
  def apply(self, state):
    return State(merge_dicts(state.values, self.effects))
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
class Inference(Operator): cost = 0
class Axiom(Operator): cost = 0

###########################################################################

def apply_image(state, operator):
  image_values = dict(state.values) # NOTE - doesn't consider implicit values
  for v, val in operator.cond():
    assert image_values.get(v, val) == val
    image_values[v] = val
  for v, val in operator.eff():
    image_values[v] = val
  return State(image_values)

def apply_preimage(partial_state, operator):
  preimage_values = dict(partial_state.conditions) # NOTE - doesn't consider implicit values
  for v, val in operator.eff():
    assert preimage_values.get(v, val) == val
    if v in preimage_values:
      del preimage_values[v]
  for v, val in operator.cond():
    assert preimage_values.get(v, val) == val
    preimage_values[v] = val
  return Goal(preimage_values)

###########################################################################

# NOTE - remember that preconditions and effects can be seen more symmetrically if a precondition must be an effect when not overwritten
def image(state, operators):
  image_state = state.values.copy() # NOTE - doesn't consider implicit values
  for operator in operators:
    for v, val in operator.pre():
      assert image_state.get(v, default=val) == val
      image_state[v] = val
    for v, val in operator.eff():
      image_state[v] = val
  return image_state

def preimage(state, operators):
  preimage_state = state.values.copy() # NOTE - doesn't consider implicit values
  for operator in operators:
    for v, val in operator.eff():
      assert preimage_state.get(v, default=val) == val
      if v in preimage_state:
        del preimage_state[v]
    for v, val in operator.pre():
      assert preimage_state.get(v, default=val) == val
      preimage_state[v] = val
  return preimage_state
