from planner.state_space import Plan
from sas.states import Goal
from copy import deepcopy

# TODO
# - Plan space search as the primative search routine
# - Connect each intermediate subproblem on each level. The plan can choose to make the higher level action to transition to the next waypoint
# - Open queue of each plan for the hierarchy
# - Heuristic to achieve the next subgoal (may also encourage reaching the context-state (image) or pre-image)

# TODO - should the levels allow all actions above them or should the try to first resolve the messed up preconditions separately?
# TODO - do the Partial-Order Planning Hierarchy which simply chooses the order to refine preconditions
# TODO - recursively apply the hierarchy with the new goals identified - I guess this is what this goes already
# NOTE - can always make the argument that there is a complete version of this, but use the incomplete one instead
# TODO - specify arbitrary partial ordering on not only constraint schemas themselves but instantiations (although is good to plan for several together)
# NOTE - fewer problems if we assume the state-space is invertible
# NOTE - we are making the assumption upon each refinement that there exists a solution that uses these operators in sequence
# NOTE - we could treat each subproblem indepdently if we assume that we will eventually generate all solutions
# NOTE - even for discrete problems, cannot enumerate all plans (infinite plan-space)

"""
hierarchy = [
  {'objA', 'objB'},
  {'robot'}
]

hierarchy = defaultdict(int)
hierarchy['robot'] = 1
"""
# TODO - specify partial ordering to make DAG. Can then deduce level from BFS
# NOTE - could always not defer base positions, but defer sampling of the trajectory for the preconditions
#def pp_hierarchy_level((v, val)):
def pp_hierarchy_level(cond, operator):
  v, val = cond
  if v == 'robot':
    return 1
  return 0

# NOTE - previously used closed-world state to indicate that deferred preconditions
# NOTE - doesn't use backtracking of any kind
# TODO
# - What does it means if effects aren't deferred but preconditions are?
# - Never defer anything wrt the goal? But the goal can be treated as an operator that achieves a single goal value
#   - Can always choose to handle preconditions differently per operator/goal
#   - By deferring goal preconditions, I do think you are asserting that you can achieve them after the last operator...
#   - Maybe each invocation of an operator/condition is on a different level of deferral in the recursion

# Example where the robot must move it's base to do a pick (deferred computation) but must press button first to open door
# Start -> Pick -> Goal
# Start -> Move1 -> Pick
# Start -> Press -> Move1
# Start -> Move2 -> Press
# Press -> Move3 -> Move1???
# If I planned for all the sublevels at once, this wouldn't have happened
# Well I guess it depends on if I am deferring the move action itself or checking feasibility?
# Don't think there is any way to defer either moving and feasibility and not end up with a suboptimal plan
# Ideally, the hierarchy should be used sparingly if the heuristic search is the primarily search control

# TODO
# - Should I plan in context-states with preconditions!!!!!!!!!
#   - Yes! This imposes additional constraints on the high-level search to understand orderings
#   - Otherwise, more likely that the way you achieve a an action renders the rest of the plan infeasible
# - What if preconditions are have deferred computation?
#   - This makes it more likely that the high-level plan is unresolvable, but still could be okay
# - Would I ever want something like this for preimages?
# - Would it ever be advantageous to defer effects?
# - What is the leverage of hierarchy then?
#   - It shortens the horizon by deferring preconditions where you know you can fill in the dots
#   - Allows for operators to not be fully constructed (which is expensive in TAMP)
# - I think I wasn't doing this before. Instead, I was just ignoring a full variable when planning
#   - I guess ignoring a full variable is another strategy to do this. Including side-effects makes planning harder
#   - Additionally, the previous version wasn't recursive in the same way. It wouldn't start the hierarchy from scratch
# - I mean achieving something could always require some sort of prevent future effects side effect anyways

def fixed_search(start, goal, operators, subsearch, hierarchy, level=0):
  # Modify operators wrt hierarchy but not goal?
  # Can always modify operators to produce additional effects from the projected preconditions

  modified_operators = []
  #for operator in operators + [goal]: # TODO - include goal
  for operator in operators:
    modified_operator = deepcopy(operator)
    modified_operator.original = operator
    for v, val in operator.cond():
      if v not in operator.effects: # NOTE - adds operator image
        modified_operator.effects[v] = val
      if hierarchy((v, val), operator) > level:
        del modified_operator.conditions[v]
    modified_operators.append(modified_operator)

  plan, state_space = subsearch(start, goal, modified_operators)
  #print(plan.length)
  if plan is None:
    return None, None

  state = start
  sequence = []
  #for operator in plan.operators + [goal]: # TODO - should I assume that the last operator achieves the goal or not?
  for modified_operator in plan.operators:
    operator = modified_operator.original
    if state not in operator:
      #print(state, operator)
      #print()
      subplan, subdata = fixed_search(state, Goal(operator.conditions), operators, subsearch, hierarchy, level=level+1)
      if subplan is None:
        return None, None
      state = subplan.get_states()[-1]
      sequence += subplan.operators
    if operator != goal:
      state = operator(state)
      sequence.append(operator)
  return Plan(start, sequence), None # TODO - merge state-spaces

# TODO - some sort of recursion here on the subproblem in the event that the plan is satisfiable using a fair amount of preconditions
# While the plan to achieve the goal is empty, increase the level? As soon as you get something, then you continue
# Maybe there really is only one level which iterates upon the plan being trivially solved or something
def recursive_search(start, goal, operators, subsearch, hierarchy, level=0, goal_level=0):
  raise NotImplementedError()
  plan, state_space = subsearch(start, goal, operators)
  if plan is None:
    return None, None

  state = start
  sequence = []
  #for operator in plan.operators + [goal]: # TODO - should I assume that the last operator achieves the goal or not?
  for operator in plan.operators:
    if state not in operator:
      print(state, operator)
      subgoal = Goal(operator.conditions) # Goal-level different than new operator level or something
      subplan, subdata = recursive_search(state, subgoal, operators, subsearch, hierarchy, level=level+1)
      #subplan, subdata = recursive_search(state, subgoal, operators, subsearch, hierarchy, level=0, goal_level=level+1) # TODO - parent level?
      if subplan is None:
        return None, None
      state = subplan.get_states()[-1]
      sequence += subplan.operators
    if operator != goal:
      state = operator(state)
      sequence.append(operator)
  return Plan(start, sequence), None # TODO - merge state-spaces
