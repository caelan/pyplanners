from operators import Pick, Place, Stack, Unstack
from discrete.schedulers import InitDiscreteScheduler, CallDiscreteScheduler, \
  SubplannerDiscreteScheduler, SeparateSubplannerDiscreteScheduler
from planner.states import State, Substate, PartialState
from planner.conditions import SubstateCondition
from misc.functions import merge_dicts
from itertools import permutations

def restack(n=10, height=5):
  blocks = ['B%d'%i for i in range(1, n+1)]
  start = State(merge_dicts(
      {('on', blocks[0]): 'table', ('clear', blocks[height-1]): True},
      {('on', blocks[i+1]): blocks[i] for i in range(height-1)},
      {('on', blocks[i]): 'table' for i in range(height, n)},
      {('clear', blocks[i]): True for i in range(height, n)}
  ))

  goal = PartialState([
    SubstateCondition(Substate({('on', blocks[i]): blocks[i+1]})) for i in range(height-1)] + [
    SubstateCondition(Substate({('on', blocks[height-1]): 'table'}))
  ])

  actions = [Pick(item) for item in blocks] + [Place(item) for item in blocks] + \
    [Unstack(*item) for item in permutations(blocks, 2)] + [Stack(*item) for item in permutations(blocks, 2)]

  return start, goal, lambda rg: InitDiscreteScheduler(rg, actions)
  #return start, goal, lambda rg: CallDiscreteScheduler(rg, actions)
  #return start, goal, lambda rg: SubplannerDiscreteScheduler(rg, actions)
  #return start, goal, lambda rg: SeparateSubplannerDiscreteScheduler(rg, actions)
