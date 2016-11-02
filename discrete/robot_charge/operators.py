import inspect

from planner.domains import *
from planner.subsets import *
from planner.operators import *

class Move(Action):
  name, cost = 'Move', 1
  def __init__(self, initial, final):
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    Action.__init__(self, {arg: values[arg] for arg in args if arg not in ['self']})
    self.transitions = {
      'robot': Transition(initial, final),
    }

class MoveCharge(Action):
  name, cost = 'MoveCharge', 1
  def __init__(self, initial, final, charge):
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    Action.__init__(self, {arg: values[arg] for arg in args if arg not in ['self']})
    self.transitions = {
      'robot': Transition(initial, final),
      'charge': Transition('+' if charge == '-' else '-', charge)
    }

def initialize():
  # Start State
  start = State({
    'robot': 'A',
    'charge': '-'
  })

  # Goal State
  goal = PartialState({
    'robot': FiniteSubset(set(['B', 'C'])),
    'charge': Value('+')
  })

  actions = [
    Move('A', 'B'),
    Move('B', 'A'),
    MoveCharge('B', 'D', '+'),
    MoveCharge('D', 'B', '-'),
    Move('A', 'C'),
    Move('C', 'A'),
    Move('C', 'D'),
    Move('D', 'C'),
  ]

  return start, goal, ConnectivityGraph(create_discrete_domains(actions))

