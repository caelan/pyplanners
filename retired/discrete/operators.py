from planner.conditions import SubstateCondition
from planner.effects import ValueEffect
from planner.states import Substate

def add_operator_transitions(operator, transitions):
  for variable, (start, end) in transitions.items():
    if start is not None:
      operator.conditions.append(SubstateCondition(Substate({variable: start})))
    if end is not None:
      operator.effects[variable] = ValueEffect(end)

def is_discrete_condition(condition):
  return isinstance(condition, SubstateCondition) and len(condition.substate) == 1

def is_discrete_effect(effect):
  return isinstance(effect, ValueEffect)

def is_discrete_operator(operator):
  for condition in operator.conditions:
    if not is_discrete_condition(condition):
      return False
  for _, effect in operator.effects.items():
    if not is_discrete_effect(effect):
      return False
  return True

def connect_discrete_conditions(rg, edge):
  for connector in edge.connectors:
    if is_discrete_condition(connector.condition):
      vertex = rg.vertex(connector.condition.substate)
      vertex.connect(connector)
      if rg.start.substate in connector.condition:
        rg.start.connect(connector)

def connect_discrete_effects(rg, edge):
  for variable, effect in edge.value.effects.items():
    if is_discrete_effect(effect):
      vertex = rg.vertex(Substate({variable: effect.value}))
      edge.connect(vertex)

def connect_discrete_operator(rg, edge):
  connect_discrete_conditions(rg, edge)
  connect_discrete_effects(rg, edge)
