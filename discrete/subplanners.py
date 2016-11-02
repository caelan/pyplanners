from planner.subplanners import Subplanner
from operators import is_discrete_effect

class DiscreteSubplanner(Subplanner):
  def __init__(self, operators):
    self.operators = operators
  def generator(self, start_vertex, goal_connector, rg):
    #yield # NOTE - include if don't want initial generation
    vertex = rg.vertex(goal_connector.condition.substate)
    vertex.connect(goal_connector)
    variable, value = list(vertex.substate)[0]

    for operator in self.operators:
      if variable in operator.effects:
        effect = operator.effects[variable]
        if is_discrete_effect(effect) and effect.value == value:
          rg.edge(operator).connect(vertex)
    yield
