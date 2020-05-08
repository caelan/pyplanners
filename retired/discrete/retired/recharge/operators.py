import inspect

from planner.domains import *
from planner.subsets import *
from blocks_world import *


# TODO
# - consider supporting actions that change a non-controlled variable by a specified amount
# - serialize planning task described in the numeric way (action for increasing/decreasing a value)

class Forward(Action):
  name, cost = 'Forward', 1
  def __init__(self, position, charge):
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    Action.__init__(self, {arg: values[arg] for arg in args if arg not in ['self']})
    self.transitions = {
      'position': Transition(position, position + 1),
      'charge': Transition(charge, charge - 2),
    }

class Backward(Action):
  name, cost = 'Backward', 1
  def __init__(self, position, charge):
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    Action.__init__(self, {arg: values[arg] for arg in args if arg not in ['self']})
    self.transitions = {
      'position': Transition(position, position - 1),
      'charge': Transition(charge, charge - 1),
    }

class Recharge(Action):
  name, cost = 'Recharge', 1
  def __init__(self, charge):
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    Action.__init__(self, {arg: values[arg] for arg in args if arg not in ['self']})
    self.transitions = {
      'charge': Transition(charge, charge + 1)
    }


class Switch(Action):
  name, cost = 'Switch', 1
  def __init__(self, position, charge):
    args, _, _, values = inspect.getargvalues(inspect.currentframe())
    Action.__init__(self, {arg: values[arg] for arg in args if arg not in ['self']})
    self.transitions = {
      'switch': Transition(False, True),
      'charge': Transition(charge, 0)
    }
    self.subsets = {
      'position': Value(position)
    }

class PositionDomain(Domain):
  variable = 'position'
  def __init__(self):
    Domain.__init__(self)

  class Controller(Domain.Controller):
    def __init__(self, domain, start, goal, reachability_graph):
      Domain.Controller.__init__(self, domain, start, goal, reachability_graph)
      charge = max(reachability_graph.start.get('charge'), 1)
      position = start
      while not goal.contains(position):
        action = Forward(position, charge) if start < goal.value else Backward(position, charge)
        position = action.end(self.variable)
        self.add_action(action)
      self.exhausted = True
    def drive(self):
      raise RuntimeError('PositionDomain is always exhausted')

class ChargeDomain(Domain):
  variable = 'charge'
  def __init__(self):
    Domain.__init__(self)

  class Controller(Domain.Controller):
    def __init__(self, domain, start, goal, reachability_graph):
      Domain.Controller.__init__(self, domain, start, goal, reachability_graph)
      charge = start
      while not goal.contains(charge):
        action = Recharge(charge)
        charge = action.end(self.variable)
        self.add_action(action)
      self.exhausted = True
    def drive(self):
      raise RuntimeError('ChargeDomain is always exhausted')

def initialize():
  # Start State

  start = State({
    'position': 0,
    'charge': 2,
    'switch': False
  })

  # Goal State
  goal = PartialState({
    'position': Value(0),
    'switch': Value(True)
  })

  return start, goal, ConnectivityGraph([PositionDomain(), ChargeDomain(), BasicDiscreteDomain('switch', [Switch(5, 3)])])
