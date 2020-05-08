from .subplanners import DiscreteSubplanner
from .operators import is_discrete_condition, is_discrete_effect, is_discrete_operator, \
  connect_discrete_conditions, connect_discrete_operator


class Scheduler(object):
  def __init__(self, rg):
    self.rg = rg
  def __call__(self, start_vertex, connector):
    raise NotImplementedError('Scheduler must implement __call__(self, start_vertex, connector)')

class GeneratingScheduler(Scheduler):
  def __init__(self, rg, subplanners):
    super(self.__class__, self).__init__(rg)
    self.subplanners = subplanners
  def __call__ (self, start_vertex, connector):
    return [subplanner(start_vertex, connector, self.rg) for subplanner in self.subplanners
            if subplanner.applicable(start_vertex, connector, self.rg)]

###########################################################################

class InitDiscreteScheduler(Scheduler):
  def __init__(self, rg, operators):
    super(self.__class__, self).__init__(rg)
    self.rg.goal.intermediates.update(self.rg.goal.connectors) # NOTE - marks as intermediates to prevent growing
    connect_discrete_conditions(self.rg, self.rg.goal)
    for operator in operators:
      if not is_discrete_operator(operator):
        raise RuntimeError(self.__class__.__name__ + ' passed non-discrete operator')
      edge = self.rg.edge(operator)
      edge.intermediates.update(edge.connectors)
      connect_discrete_operator(self.rg, edge)
  def __call__(self, start_vertex, goal_connector):
    return []

class CallDiscreteScheduler(Scheduler):
  def __init__(self, rg, operators):
    super(self.__class__, self).__init__(rg)
    self.operators = operators
  def __call__(self, start_vertex, goal_connector):
    assert is_discrete_condition(goal_connector.condition)

    vertex = self.rg.vertex(goal_connector.condition.substate)
    vertex.connect(goal_connector)
    variable, value = list(vertex.substate)[0]

    for operator in self.operators:
      if variable in operator.effects:
        effect = operator.effects[variable]
        if is_discrete_effect(effect) and effect.value == value:
          self.rg.edge(operator).connect(vertex)
    return []

class SubplannerDiscreteScheduler(Scheduler):
  def __init__(self, rg, operators):
    super(self.__class__, self).__init__(rg)
    self.subplanner = DiscreteSubplanner(operators)
  def __call__(self, start_vertex, goal_connector):
    return [self.subplanner(start_vertex, goal_connector, self.rg)]

class SeparateSubplannerDiscreteScheduler(Scheduler):
  def __init__(self, rg, operators):
    super(self.__class__, self).__init__(rg)
    self.operators = operators
  def __call__(self, start_vertex, goal_connector):
    assert is_discrete_condition(goal_connector.condition)

    vertex = self.rg.vertex(goal_connector.condition.substate)
    vertex.connect(goal_connector)
    variable, value = list(vertex.substate)[0]

    subplanners = []
    for operator in self.operators:
      if variable in operator.effects:
        effect = operator.effects[variable]
        if is_discrete_effect(effect) and effect.value == value:
          subplanners.append(DiscreteSubplanner([operator])(start_vertex, goal_connector, self.rg))
    return subplanners
