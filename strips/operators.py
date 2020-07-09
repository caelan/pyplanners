from .states import State
from misc.objects import str_object

class Operator(object):
    cost = None
    def __init__(self, args):
        for k, v in args.items():
            setattr(self, k, v)
        self.args = args # TODO - use FrozenDict instead
        self._frozen_args = frozenset(args.items())
        self._hash = None
        self.conditions = None
        self.effects = None
        self.test = lambda state: True
    def applicable(self, state):
        return all(literal in state for literal in self.conditions) #and self.test(state)
    __contains__ = applicable
    def apply(self, state):
        # TODO: cancellation semantics
        return State({atom for atom in state.atoms if atom.negate() not in self.effects} |
                     {literal for literal in self.effects if not literal.negated})
    def dump(self):
        print('{}\npre: {}\neff: {}\ncost: {}'.format(self, self.conditions, self.effects, self.cost))
    def __call__(self, state):
        return self.apply(state) if self.applicable(state) else None
    def is_axiom(self):
        return isinstance(self, Axiom)
    def __iter__(self):
        yield self
    def __len__(self):
        return 1
    def __eq__(self, other):
        return (type(self) == type(other)) and (self._frozen_args == other._frozen_args)
    def __ne__(self, other):
        return not (self == other)
    def __hash__(self):
        if self._hash is None:
            self._hash = hash((self.__class__, self._frozen_args))
        return self._hash
    def __str__(self):
        return self.__class__.__name__ + str_object(self.args)
    __repr__ = __str__

class Action(Operator): 
    cost = 1
class Axiom(Operator): 
    cost = 0
