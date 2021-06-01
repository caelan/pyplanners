from strips.operators import Action
from strips.states import State, PartialState, Literal, STRIPSProblem
from misc.utils import arg_info, currentframe
from misc.functions import pairs
from itertools import permutations

class Clear(Literal): pass
class OnTable(Literal): pass
class ArmEmpty(Literal): pass
class Holding(Literal): pass
class On(Literal): pass

class Pick(Action):
    def __init__(self, obj):
        super(self.__class__, self).__init__(arg_info(currentframe()))
        self.conditions = {Clear(obj), OnTable(obj), ArmEmpty()}
        self.effects = {Holding(obj),
                        ~Clear(obj), ~OnTable(obj), ~ArmEmpty()}

class Place(Action):
    def __init__(self, obj):
        super(self.__class__, self).__init__(arg_info(currentframe()))
        self.conditions = {Holding(obj)}
        self.effects = {Clear(obj), OnTable(obj), ArmEmpty(),
                        ~Holding(obj)}

class Stack(Action):
    def __init__(self, obj, under_obj):
        super(self.__class__, self).__init__(arg_info(currentframe()))
        self.conditions = {Holding(obj), Clear(under_obj)}
        self.effects = {Clear(obj), ArmEmpty(), On(obj, under_obj),
                        ~Holding(obj), ~Clear(under_obj)}

class Unstack(Action):
    def __init__(self, obj, under_obj):
        super(self.__class__, self).__init__(arg_info(currentframe()))
        self.conditions = {Clear(obj), ArmEmpty(), On(obj, under_obj)}
        self.effects = {Holding(obj), Clear(under_obj),
                        ~Clear(obj), ~ArmEmpty(), ~On(obj, under_obj)}

###########################################################################

def line_stack_blocks(n=10, height=5):
    height = max(height, 0)
    n = max(height, n)
    blocks = ['Block{}'.format(i) for i in range(1, n+1)]

    operators = [Pick(item) for item in blocks] + \
        [Place(item) for item in blocks] + \
        [Unstack(*item) for item in permutations(blocks, 2)] + \
        [Stack(*item) for item in permutations(blocks, 2)]

    initial = State({OnTable(block) for block in blocks} |
                    {Clear(block) for block in blocks} |
                    {ArmEmpty()})

    tower = blocks[:height]
    goal = PartialState({OnTable(blocks[0]), ArmEmpty()} |
                        {On(obj, under_obj) for under_obj, obj in pairs(tower)})

    return STRIPSProblem(initial, goal, operators)

def restack_blocks(n=4, height=4):
    height = max(height, 0)
    n = max(height, n)
    blocks = ['Block{}'.format(i) for i in range(1, n+1)]

    operators = [Pick(item) for item in blocks] + \
        [Place(item) for item in blocks] + \
        [Unstack(*item) for item in permutations(blocks, 2)] + \
        [Stack(*item) for item in permutations(blocks, 2)]

    tower = blocks[:height]
    table = blocks[height:]
    initial = State({OnTable(blocks[height-1]), ArmEmpty(), Clear(blocks[0])} |
                    {On(obj, under_obj) for under_obj, obj in pairs(tower[::-1])} |
                    {OnTable(block) for block in table} |
                    {Clear(block) for block in table})

    goal = PartialState({OnTable(blocks[0]), ArmEmpty()} |
                        {On(obj, under_obj) for under_obj, obj in pairs(tower)})

    return STRIPSProblem(initial, goal, operators)

###########################################################################

PROBLEMS = [
    line_stack_blocks,
    restack_blocks,
]
