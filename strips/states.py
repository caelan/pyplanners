from misc.objects import str_object

class Literal(object):
    def __init__(self, *args):
        self.args = tuple(args)
        self.sign = True
    def copy(self):
        new = self.__class__(*self.args)
        new.sign = self.sign
        return new
    def __abs__(self):
        new = self.copy()
        new.sign = True
        return new
    def __neg__(self):
        new = self.copy()
        new.sign = False
        return new
    def __invert__(self):
        new = self.copy()
        new.sign = not self.sign
        return new
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
    def __contains__(self, literal):
        return literal.sign == (abs(literal) in self.atoms)
    def __eq__(self, other):
        return type(self) == type(other) and self.atoms == other.atoms
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
    def __contains__(self, state):
        return all(literal in state for literal in self.conditions)
    def __eq__(self, other):
        return (type(self) == type(other)) and (self.conditions == other.conditions)
    def __ne__(self, other):
        return not (self == other)
    def __hash__(self):
        return hash((self.__class__, self.conditions))
    def __str__(self):
        return self.__class__.__name__ + str_object(self.conditions)
    __repr__ = __str__
