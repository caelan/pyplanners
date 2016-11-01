from miscellaneous import *
from crg_searches import *
from itertools import product
import crg_heuristics

class ActionsOracle:
  def __init__(self, start, goal, actions):
    self.actions = actions
    self.values_to_actions = {}
    self.variable_sets = set()
    for action in actions:
      key = frozenset(action.preconditions.values.iteritems())
      if key not in self.values_to_actions:
        self.values_to_actions[key] = []
      self.values_to_actions[key].append(action)

      v_key = frozenset(action.preconditions.values.keys())
      self.variable_sets.add(v_key)

    self.precondition_to_actions = {}
    self.effect_to_actions = {}
    for action in actions:
      for p in action.preconditions.values:
        if (p, action.preconditions.values[p]) not in self.precondition_to_actions:
          self.precondition_to_actions[(p, action.preconditions.values[p])] = []
        self.precondition_to_actions[(p, action.preconditions.values[p])].append(action)

      for e in action.effects:
        if (e, action.effects[e]) not in self.effect_to_actions:
          self.effect_to_actions[(e, action.effects[e])] = []
        self.effect_to_actions[(e, action.effects[e])].append(action)

    self.distance_cache = [{} for v in range(len(start.values))]

    return

    ###############################

    #Causal Graph (Seperability includes ancestors and co-effects)
    self.causal_edges = []
    for v in range(len(start.values)):
      self.causal_edges.append([0 for e in range(len(start.values))])

    for action in actions:
      edges = set()
      for v in action.preconditions.values.keys() + action.preconditions.fns.keys():
        for e in action.effects:
          if (v, e) not in edges:
            self.causal_edges[v][e] += 1
            edges.add((v, e))

      for e1 in action.effects:
        for e2 in action.effects:
          if e1 != e2 and (e1, e2) not in edges:
            self.causal_edges[e1][e2] += 1
            edges.add((e1, e2))

    print 'Full Causal Graph'
    print self.causal_edges

    strongly_connected_componets = []
    global visited, stack
    visited = 0
    index = {}
    low_link = {}
    stack = []

    def strong_connect(v):
      global visited, stack
      index[v] = visited
      low_link[v] = visited
      visited += 1
      stack.append(v)

      for w in range(len(self.causal_edges[v])):
        if self.causal_edges[v][w] != 0:
          if w not in index:
            strong_connect(w)
            low_link[v] = min(low_link[v], low_link[w])
          elif w in stack:
            low_link[v] = min(low_link[v], index[w])

      if index[v] == low_link[v]:
        strongly_connected_componets.append(stack[stack.index(v):])
        stack = stack[:stack.index(v)]

    for v in range(len(self.causal_edges)):
      if v not in index:
        strong_connect(v)

    print 'Strongly Connected Components'
    print strongly_connected_componets

    for c in range(len(strongly_connected_componets)):
      component = strongly_connected_componets[c]
      weights = {}
      for end in component:
        weights[end] = 0
        for start in component:
          if start != end:
            weights[end] += self.causal_edges[start][end]
      strongly_connected_componets[c] = sorted(component, key = lambda v: weights[v])

      for s in range(len(strongly_connected_componets[c])): #TODO - not quite right, need to reevaulate the ordering given the removed edges each time
        for e in range(s + 1):
          self.causal_edges[strongly_connected_componets[c][s]][strongly_connected_componets[c][e]] = 0

    print 'Strongly Connected Components'
    print strongly_connected_componets

    print 'Prunned Casual Graph'
    print self.causal_edges

    quit()

  def relevant_actions(self, state):
    relevant_actions = []
    for variables in self.variable_sets:
      key = frozenset([(v, state.values[v]) for v in variables])
      if key in self.values_to_actions:
        relevant_actions.extend(self.values_to_actions[key])
    return relevant_actions
  def relevant_relaxed_actions(self, variable, value, current_variables):
    relevant_actions = []
    for variables in self.variable_sets:
      if variable not in variables: continue

      for tup in product(*([[(variable, value)]] + [map(lambda val: (v, val), current_variables[v].keys()) for v in variables if v != variable])):
        key = frozenset(tup)
        if key in self.values_to_actions:
          relevant_actions.extend(self.values_to_actions[key])

    return relevant_actions

  def distance(self, v, start, end): #TODO - Use backwards/bidirectonal search
    if start == end:
      return 0
    if v != 0: #Don't current suppor the other things
      return 1

    if (start, end) in self.distance_cache[v]:
      return self.distance_cache[v][(start, end)]

    queue = [start]
    visited = {start: 0}
    while len(queue) > 0:
      node = queue.pop(0)

      for action in self.precondition_to_actions[(v, node)]:
        if v in action.effects:
          next = action.effects[v]
          if next not in visited:
            queue.append(next)
            visited[next] = visited[node] + 1
            if next == end:
              self.distance_cache[v][(start, end)] = visited[next]
              self.distance_cache[v][(end, start)] = visited[next]
              return visited[next]

    return None


def plan(start, goal, actions, parameters = {
    'SEARCH': ('best_first', {'OPTIMAL': False, 'SCALE': None}),
    'HEURISTIC': 'ff',
    'HELPFUL_ACTIONS': 'all',
    'MAX_TIME': None,
    'MAX_ITERATIONS': None,
    'VERBOSE': True
  }):

  """
  parameters = {
    'SEARCH': 'hill_climbing', #best_first | hill_climbing
    'USE_HEURISTIC': 'ffrob_bias', #no | naive | reachable | placements | goal_placements | ff | ffree | maxrob | addrob | ffrob | ffrob_bias
    'HELPFUL_ACTIONS': False,
    'HEURISTIC_SCALE': None, #None makes it greedy
    'STEEPEST': True
  }"""

  SEARCH = parameters['SEARCH'][0] #best_first | hill_climbing
  HEURISTIC = parameters['HEURISTIC'] #0 | naive | reachable | placements | goal_placements | ff | ffree | maxrob | addrob | ffrob | ffrob_bias
  HELPFUL_ACTIONS = parameters['HELPFUL_ACTIONS'] #all | first_goals | first_actions
  MAX_TIME = parameters['MAX_TIME'] if 'MAX_TIME' in parameters else None #TODO - use python magic to only include these arguments if they are included in parameters
  MAX_ITERATIONS = parameters['MAX_ITERATIONS'] if 'MAX_ITERATIONS' in parameters else None
  VERBOSE = parameters['VERBOSE'] if 'VERBOSE' in parameters else True

  #HEURISTIC_SCALE = parameters['HEURISTIC_SCALE']
  #STEEPEST = parameters['STEEPEST']

  actions_oracle = ActionsOracle(start, goal, actions)

  heuristic = lambda state: getattr(crg_heuristics, 'h_' + HEURISTIC)(state, goal, actions_oracle)
  helpful_actions = getattr(crg_heuristics, 'ha_' + HELPFUL_ACTIONS)

  print
  print '---------------------------------------------------------------------------------------'
  print
  print 'Solving Planning Task'
  print

  if SEARCH == 'best_first':
    (plan, iterations, run_time) = best_first_search(start, goal, actions_oracle, heuristic, helpful_actions)
  elif SEARCH == 'hill_climbing':
    (plan, iterations, run_time) = hill_climbing_search(start, goal, actions_oracle, heuristic, helpful_actions)
  else:
    assert False

  #global crg_heuristics.total_actions_processed, crg_heuristics.total_plan_graph_size, crg_heuristics.total_plan_graph_uses
  print crg_heuristics.total_actions_processed, crg_heuristics.total_plan_graph_values, crg_heuristics.total_plan_graph_actions, crg_heuristics.total_plan_graph_uses
  print float(crg_heuristics.total_plan_graph_values)/crg_heuristics.total_plan_graph_uses, float(crg_heuristics.total_plan_graph_actions)/crg_heuristics.total_plan_graph_uses, float(crg_heuristics.total_actions_processed)/crg_heuristics.total_plan_graph_uses


  print '---------------------------------------------------------------------------------------'
  print
  if not plan:
    print 'Could not find plan. Took', run_time, 'seconds with', iterations, 'states explored'
    print
  else:
    (sequence, cost) = plan
    print 'Found plan of cost ' + str(cost) + '. Took', run_time, 'seconds with', iterations, 'states explored'
    print

    step = 1
    for (action, state) in sequence:
      if action is not None:
        print 'Action', step, '|', action
        print
        step += 1

  print 'Done!'
  print

  return (plan, iterations, run_time)
