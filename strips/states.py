from collections import namedtuple
from misc.objects import str_object

class Literal(object):
    def __init__(self, *args):
        self.args = tuple(args)
        self.sign = True
    @property
    def negated(self):
        return not self.sign
    def copy(self):
        new = self.__class__(*self.args)
        new.sign = self.sign
        return new
    def positive(self):
        new = self.copy()
        new.sign = True
        return new
    __abs__ = positive # abs(literal)
    def negate(self):
        new = self.copy()
        new.sign = not self.sign
        return new
    __neg__ = negate # -literal
    __invert__ = negate # ~literal
    def __iter__(self):
        return iter(self.args)
    def __eq__(self, other):
        return (type(self) == type(other)) and (self.sign == other.sign) and (self.args == other.args)
    def __ne__(self, other):
        return not (self == other)
    def __hash__(self):
        return hash((self.__class__, self.args, self.sign))
    def __lt__(self, other):
        return id(self) < id(other)
    def __str__(self):
        s = self.__class__.__name__ + str_object(self.args)
        return s if self.sign else 'not {}'.format(s)
    __repr__ = __str__

class State(object):
    def __init__(self, atoms, external=None):
        self.atoms = frozenset(atoms)
        self.external = external
        # TODO: refine function where external is updated
        # TODO: should I assume external is hashable?
    def identity(self):
        return self.__class__, frozenset(self.__dict__.items())
    def holds(self, literal):
        return literal.negated == (literal.positive() not in self.atoms)
    __contains__ = holds
    def __iter__(self):
        return iter(self.atoms)
    def __eq__(self, other):
        return (type(self) == type(other)) and (self.identity() == other.identity())
    def __ne__(self, other):
        return not (self == other)
    def __hash__(self):
        return hash(self.identity())
    def __str__(self):
        #return '{}({})'.format(self.__class__.__name__, id(self))
        return self.__class__.__name__ + str_object(self.atoms)
    __repr__ = __str__

class PartialState(object):
    def __init__(self, literals, test=lambda state: True):
        self.conditions = frozenset(literals)
        self.test = test # TODO: cache the test results
    def contains(self, state):
        return all(literal in state for literal in self.conditions) # and self.test(state)
    __contains__ = contains
    def __iter__(self):
        return iter(self.conditions)
    def __eq__(self, other):
        return (type(self) == type(other)) and (self.conditions == other.conditions)
    def __ne__(self, other):
        return not (self == other)
    def __hash__(self):
        return hash((self.__class__, self.conditions))
    def __str__(self):
        return self.__class__.__name__ + str_object(self.conditions)
    __repr__ = __str__

STRIPSProblem = namedtuple('STRIPSProblem', ['initial', 'goal', 'operators'])
