from state_expanders import *

# TODO
# - Replanning
# - Non-aggressive hierarchy (allowing open subproblems)
# - Other factored planning

def search(start, goal, hierarchy, level=0):
  level_start = State({v: start.get(v) for v in start.values
                       if some(lambda item: v in item[0], hierarchy[:level + 1])})

  print('-----------------------------------------------------------------\n')

  print(level, level_start, goal)
  plan, data = hierarchy[level][1](level_start, goal)


  time, iterations, states = data.time, data.iterations, data.states
  if plan is None: return None, planner.main.SearchData(time, iterations, states)


  print([action.name for (action, _) in plan.sequence if action is not None])
  print()

  sequence = [(None, start)]
  cost, length = plan.cost, plan.length
  for action, _ in plan.sequence:
    if action is not None:
      current_state = sequence[-1][1]
      if not action.applicable(current_state):
        subplan, subdata = search(current_state, PartialState(action.pre()), hierarchy, level=level+1)
        time += subdata.time; iterations += subdata.iterations; states += subdata.states
        if subplan is None: return None, planner.main.SearchData(time, iterations, states)

        sequence += subplan.sequence[1:]
        cost += subplan.cost; length += subplan.length
        current_state = sequence[-1][1]
      sequence.append((action, action.apply(current_state)))
  return planner.main.Plan(sequence, cost, length), planner.main.SearchData(time, iterations, states)
