from collections import defaultdict, deque
from .states import State, PartialState
from misc.objects import str_object

# TODO: move this into a shared class
class DomainError(Exception):
    def __init__(self, salary, message="Salary is not in (5000, 15000) range"):
        self.salary = salary
        self.message = message
        super().__init__(self.message)
    # def __str__(self):
    #     return self.message

class Operator(PartialState):
    cost = None
    def __init__(self, args):
        #super(Operator, self).__init__(...)
        for k, v in args.items():
            setattr(self, k, v)
        self.args = args # TODO - use FrozenDict instead
        self._frozen_args = frozenset(args.items())
        self._hash = None
        self.conditions = None
        self.effects = None
        self.test = lambda state: True
        self.forward = lambda state: state
    # TODO: override instead?
    # def test(self, state):
    #     return True
    # def forward(self, state):
    #     return state
    applicable = PartialState.contains
    def apply(self, state):
        # TODO: cancellation semantics
        return State({atom for atom in state.atoms if atom.negate() not in self.effects} |
                     {literal for literal in self.effects if not literal.negated}, external=state.external)
    def __call__(self, state):
        #return self.apply(state) if self.applicable(state) else None
        assert self.applicable(state)
        return self.apply(state)
    def is_axiom(self):
        return isinstance(self, Axiom)
    def dump(self):
        print('{}\npre: {}\neff: {}\ncost: {}'.format(self, self.conditions, self.effects, self.cost))
    def __iter__(self):
        yield self
    def __len__(self):
        return 1
    def __eq__(self, other):
        return (type(self) == type(other)) and (self._frozen_args == other._frozen_args)
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

###########################################################################

def derive_state(state, axioms):
    # TODO: assumes there isn't any contradiction
    unprocessed = defaultdict(list)
    unsatisfied = {}
    for axiom in axioms:
        unsatisfied[axiom] = len(axiom.conditions)
        for literal in axiom.conditions:
            unprocessed[literal].append(axiom)

    reached_literals = {literal for literal in unprocessed if literal in state}
    queue = deque(reached_literals)

    def process_operator(axiom):
        for effect in axiom.effects:
            if effect not in reached_literals:
                reached_literals.add(effect)
                queue.append(effect)

    for axiom in unsatisfied:
        if unsatisfied[axiom] == 0:
            process_operator(axiom)
    while queue:
        literal = queue.popleft()
        for axiom in unprocessed[literal]:
            unsatisfied[axiom] -= 1
            if unsatisfied[axiom] == 0:
                process_operator(axiom)
        del unprocessed[literal]

    state = State({atom for atom in state.atoms if atom.negate() not in reached_literals} |
                  {literal for literal in reached_literals if not literal.negated}, external=state.external)
    axiom_plan = [] # TODO: retrace an axiom plan
    return state, axiom_plan
