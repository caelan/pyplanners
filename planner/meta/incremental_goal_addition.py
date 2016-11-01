from planner.operators import *
from planner.states import *

def incremental_goal_addition(start, goal, search): # Replace generator_fn with state_space
  start_time = time()
  operators = []
  current = start # Allow starting at start state each time
  for i in range(len(goal)):
    plan_data, _ = search(current, PartialState(goal.conditions[:i+1]))
    if plan_data is None: return None, SearchData(time() - start_time, None, None)
    operators += plan_data.operators
    current = MacroOperator(*plan_data.operators)(current)[-1]
    if current in goal: break
    print 50*'-', '\n'

  if current not in goal: return None, SearchData(time() - start_time, None, None)
  return PlanData(start, operators), SearchData(time() - start_time, None, None)
