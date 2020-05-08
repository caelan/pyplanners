from strips.operators import Action
from itertools import combinations

class SprayPaint(Action):
    actionName = 'SprayPaint'
    def __init__(self, args):
        Action.__init__(self, args)
        (obj, sprayer, color) = self.args
        self.preconditions = [('onTable', obj), ('clear', obj), ('paintsColor', sprayer, color), ('holding', sprayer)]
        self.positiveEffects = [('colored', obj, color)]
        self.negativeEffects =    []

class BrushPaint(Action):
    actionName = 'BrushPaint'
    def __init__(self, args):
        Action.__init__(self, args)
        (obj, brush, color) = self.args
        self.preconditions = [('onTable', obj), ('clear', obj), ('paintsColor', brush, color), ('holding', brush)]
        self.positiveEffects = [('colored', obj, color)]
        self.negativeEffects =    []

class LoadBrush(Action):
    actionName = 'LoadBrush'
    def __init__(self, args):
        Action.__init__(self, args)
        (brush, paintCan, color) = self.args
        self.preconditions = [('clean', brush), ('clear', paintCan), ('paintsColor', paintCan, color), ('holding', brush)]
        self.positiveEffects = [('paintsColor', brush, color)]
        self.negativeEffects = [('clean', brush)]

class WashBrush(Action):
    actionName = 'WashBrush'
    def __init__(self, args):
        Action.__init__(self, args)
        (brush, waterBucket, color) = self.args
        self.preconditions = [('clear', waterBucket), ('holding', brush), ('paintsColor', brush, color)]
        self.positiveEffects = [('clean', brush)]
        self.negativeEffects = [('paintsColor', brush, color)]

def blocks_paint_1():
        print('Paint Blocks 1')
        BLOCKS = ['blockA']
        SPRAYERS = []
        BRUSHES = ['brush']
        PAINTCANS = ['redPaintCan']
        WATERBUCKETS = []
        COLORS = ['red']
        OBJECTS = BLOCKS + SPRAYERS + BRUSHES + PAINTCANS + WATERBUCKETS

        BLOCKACTIONS = [PickUp(args) for args in combinations([OBJECTS])] +\
                        [PutDown(args) for args in combinations([OBJECTS])] +\
                        [Stack(args) for args in combinations([OBJECTS, OBJECTS])] +\
                        [Unstack(args) for args in combinations([OBJECTS, OBJECTS])]
        PAINTACTIONS = [SprayPaint(args) for args in combinations([OBJECTS, SPRAYERS, COLORS])] +\
                        [BrushPaint(args) for args in combinations([OBJECTS, BRUSHES, COLORS])] +\
                        [LoadBrush(args) for args in combinations([BRUSHES, PAINTCANS, COLORS])] +\
                        [WashBrush(args) for args in combinations([BRUSHES, WATERBUCKETS, COLORS])]
        ACTIONS = BLOCKACTIONS + PAINTACTIONS

        INITIAL = State([('onTable', 'blockA'),
                                         ('onTable', 'brush'),
                                         ('onTable', 'redPaintCan'),
                                         ('clear', 'blockA'),
                                         ('clear', 'brush'),
                                         ('clear', 'redPaintCan'),
                                         ('clean', 'brush'),
                                         ('paintsColor', 'redPaintCan', 'red'),
                                         ('armEmpty')])
        GOAL = State([('colored', 'blockA', 'red'),
                                         ('armEmpty')])

        blocksProblem = PlanProblem(INITIAL, GOAL, ACTIONS)
        blocksProblem.findPlan(maxNodes = 100000)

def blocks_paint_2():
        print('Paint Blocks 2')
        BLOCKS = ['blockA', 'blockB']
        SPRAYERS = ['blueSprayer']
        BRUSHES = ['brush']
        PAINTCANS = ['redPaintCan']
        WATERBUCKETS = ['bucket']
        COLORS = ['red', 'blue']
        OBJECTS = BLOCKS + SPRAYERS + BRUSHES + PAINTCANS + WATERBUCKETS

        BLOCKACTIONS = [PickUp(args) for args in combinations([OBJECTS])] +\
                        [PutDown(args) for args in combinations([OBJECTS])] +\
                        [Stack(args) for args in combinations([OBJECTS, OBJECTS])] +\
                        [Unstack(args) for args in combinations([OBJECTS, OBJECTS])]
        PAINTACTIONS = [SprayPaint(args) for args in combinations([OBJECTS, SPRAYERS, COLORS])] +\
                        [BrushPaint(args) for args in combinations([OBJECTS, BRUSHES, COLORS])] +\
                        [LoadBrush(args) for args in combinations([BRUSHES, PAINTCANS, COLORS])] +\
                        [WashBrush(args) for args in combinations([BRUSHES, WATERBUCKETS, COLORS])]
        ACTIONS = BLOCKACTIONS + PAINTACTIONS

        INITIAL = State([('on', 'blockB', 'blockA'),
                                         ('onTable', 'blockA'),
                                         ('onTable', 'blueSprayer'),
                                         ('onTable', 'brush'),
                                         ('onTable', 'redPaintCan'),
                                         ('onTable', 'bucket'),
                                         ('clear', 'blockB'),
                                         ('clear', 'blueSprayer'),
                                         ('clear', 'brush'),
                                         ('clear', 'redPaintCan'),
                                         ('clear', 'bucket'),
                                         ('paintsColor', 'blueSprayer', 'blue'),
                                         ('clean', 'brush'),
                                         ('paintsColor', 'redPaintCan', 'red'),
                                         ('armEmpty')])
        GOAL = State([('colored', 'blockA', 'red'),
                                    ('colored', 'blockB', 'blue'),
                                    ('armEmpty'),
                                    ('clean', 'brush')])

        blocksProblem = PlanProblem(INITIAL, GOAL, ACTIONS)
        blocksProblem.findPlan(maxNodes = 100000)

def blocks_paint_3():
        print('Paint Blocks 3')
        BLOCKS = ['blockA', 'blockB', 'blockC']
        SPRAYERS = ['redSprayer', 'blueSprayer', 'greenSprayer']
        BRUSHES = ['brush']
        PAINTCANS = ['redPaintCan', 'bluePaintCan', 'greenPaintCan']
        WATERBUCKETS = ['bucket']
        COLORS = ['red', 'blue', 'green']
        OBJECTS = BLOCKS + SPRAYERS + BRUSHES + PAINTCANS + WATERBUCKETS

        BLOCKACTIONS = [PickUp(args) for args in combinations([OBJECTS])] +\
                        [PutDown(args) for args in combinations([OBJECTS])] +\
                        [Stack(args) for args in combinations([OBJECTS, OBJECTS])] +\
                        [Unstack(args) for args in combinations([OBJECTS, OBJECTS])]
        PAINTACTIONS = [SprayPaint(args) for args in combinations([OBJECTS, SPRAYERS, COLORS])] +\
                        [BrushPaint(args) for args in combinations([OBJECTS, BRUSHES, COLORS])] +\
                        [LoadBrush(args) for args in combinations([BRUSHES, PAINTCANS, COLORS])] +\
                        [WashBrush(args) for args in combinations([BRUSHES, WATERBUCKETS, COLORS])]
        ACTIONS = BLOCKACTIONS + PAINTACTIONS

        INITIAL = State([('onTable', 'blockA'),
                                         ('onTable', 'blockB'),
                                         ('onTable', 'blockC'),
                                         ('onTable', 'redSprayer'),
                                         ('onTable', 'blueSprayer'),
                                         ('onTable', 'greenSprayer'),
                                         ('onTable', 'brush'),
                                         ('onTable', 'redPaintCan'),
                                         ('onTable', 'bluePaintCan'),
                                         ('onTable', 'greenPaintCan'),
                                         ('onTable', 'bucket'),
                                         ('clear', 'blockA'),
                                         ('clear', 'blockB'),
                                         ('clear', 'blockC'),
                                         ('clear', 'redSprayer'),
                                         ('clear', 'blueSprayer'),
                                         ('clear', 'greenSprayer'),
                                         ('clear', 'brush'),
                                         ('clear', 'redPaintCan'),
                                         ('clear', 'bluePaintCan'),
                                         ('clear', 'greenPaintCan'),
                                         ('clear', 'bucket'),
                                         ('paintsColor', 'redSprayer', 'red'),
                                         ('paintsColor', 'blueSprayer', 'blue'),
                                         ('paintsColor', 'greenSprayer', 'green'),
                                         ('clean', 'brush'),
                                         ('paintsColor', 'redPaintCan', 'red'),
                                         ('paintsColor', 'bluePaintCan', 'blue'),
                                         ('paintsColor', 'greenPaintCan', 'green'),
                                         ('armEmpty')])
        GOAL = State([('colored', 'blockA', 'red'),
                                    ('colored', 'blockB', 'blue'),
                                    ('colored', 'blockC', 'green'),
                                    ('clean', 'brush'),
                                    ('armEmpty')])

        blocksProblem = PlanProblem(INITIAL, GOAL, ACTIONS)
        blocksProblem.findPlan(maxNodes = 100000)
