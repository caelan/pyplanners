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
    def __str__(self):
        s = self.__class__.__name__ + str_object(self.args)
        return s if self.sign else 'not {}'.format(s)
    __repr__ = __str__

class State(object):
    def __init__(self, atoms):
        self.atoms = frozenset(atoms)
    def holds(self, literal):
        return literal.negated == (literal.positive() not in self.atoms)
    __contains__ = holds
    def __iter__(self):
        return iter(self.atoms)
    def __eq__(self, other):
        return (type(self) == type(other)) and (self.atoms == other.atoms)
    def __ne__(self, other):
        return not (self == other)
    def __hash__(self):
        return hash((self.__class__, self.atoms))
    def __str__(self):
        return self.__class__.__name__ + str_object(self.atoms)
    __repr__ = __str__

class PartialState(object):
    def __init__(self, literals):
        self.conditions = frozenset(literals)
    def contains(self, state):
        return all(literal in state for literal in self.conditions)
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
