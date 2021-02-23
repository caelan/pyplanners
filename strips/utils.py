from strips.ff import ff_fn, plan_cost, first_goals, h_ff_add, first_operators
from strips.hsp import h_add, h_max
from strips.operators import Action
from misc.functions import in_add, INF
from planner.progression.best_first import best_first_search, deferred_best_first_search, \
    uniform, astar, wastar2, wastar3, greedy


def h_blind(state, goal, operators):
    return 0

def h_goal(state, goal, operators):
    return sum(1 for literal in goal.conditions if literal not in state)

def h_action(state, goal, operators):
    if state in goal:
        return 0
    applicable = ha_applicable(state, goal, operators)
    if not applicable:
        return INF
    return min(operator.cost for operator in applicable)

###########################################################################

# TODO: filter out axioms

def ha_all(state, goal, operators):
    return [o for o in operators if isinstance(o, Action)]

def ha_applicable(state, goal, operators):
    return [operator for operator in ha_all(state, goal, operators) if state in operator]

def ha_sorted(state, goal, operators):
    return sorted(ha_applicable(state, goal, operators), key=lambda o: o.cost)

def ha_combine(state, goal, operators, *helpful_actions):
    seen_operators = set()
    for ha in helpful_actions:
        ha_operators = []
        for operator in ha(state, goal, operators):
            if not in_add(seen_operators, operator):
                ha_operators.append(operator)
        yield ha_operators

###########################################################################

def pair_h_and_ha(heuristic, helpful_actions):
    return lambda s, g, o: (heuristic(s, g, o), helpful_actions(s, g, o))

def combine_heuristics(*heuristics):
    return lambda s, g, o: tuple(h(s, g, o) for h in heuristics)

def combine_helpfuls(*helpfuls):
    return lambda s, g, o: [a for ha in helpfuls for a in ha(s, g, o)]

###########################################################################

# TODO: multiple cost bounds (real cost and effort)
# TODO: negative axioms
# TODO: grounding function at all

def filter_axioms(actions):
    return list(filter(lambda o: not o.is_axiom(), actions))

def single_generator(goal, operators, axioms, successors):
    #return lambda v: (yield successors(v.state, goal, operators))
    def generator(vertex):
        # TODO: a generator that regrounds at each state based on the current static facts
        state = vertex.state
        #state = vertex.derived_state # NOTE: not "safe"
        heuristic, helpful_actions = successors(state, goal, operators + axioms)
        #helpful_actions = list(filter(lambda op: op not in axioms, helpful_actions))
        helpful_actions = filter_axioms(helpful_actions)
        # NOTE - the first_actions should be anything applicable in derived_state
        yield heuristic, helpful_actions
    return generator, axioms

###########################################################################

SEARCHES = {
    #'astar': best_first_search,
    'eager': best_first_search,
    'lazy': deferred_best_first_search,
}

# TODO: populate programmatically
EVALUATORS = {
    'dijkstra': uniform,
    'astar': astar,
    'wastar2': wastar2,
    'wastar3': wastar3,
    'greedy': greedy,
}

HEURISTICS = {
    'blind': h_blind,
    'goal': h_goal,
    'max': h_max,
    'add': h_add,
    'ff': h_ff_add,
}

SUCCESSORS = {
    'all': ha_applicable, # ha_all | ha_applicable
    #'ff': first_goals, # first_operators # TODO: make a wrapper
}

###########################################################################

def lookup_heuristic(heuristic):
    if callable(heuristic):
        return heuristic
    if heuristic not in HEURISTICS:
        raise RuntimeError('Unknown heuristic: {}'.format(heuristic))
    return HEURISTICS[heuristic]

def solve_strips(initial, goal, operators, axioms=[], search='eager', evaluator='greedy',
                 heuristic='ff', successors='all', **kwargs):
    search_fn = SEARCHES[search]
    evaluator_fn = EVALUATORS[evaluator]
    if heuristic == successors == 'ff':
        combined_fn = ff_fn(plan_cost, first_goals, op=sum)
    else:
        if isinstance(heuristic, str):
            heuristic_fn = lookup_heuristic(HEURISTICS[heuristic])
        else:
            heuristic_fn = combine_heuristics(*map(lookup_heuristic, heuristic))
        if isinstance(successors, str):
            successor_fn = SUCCESSORS[successors]
        elif callable(successors):
            successor_fn = successors
        else:
            successor_fn = combine_helpfuls(*successors)
        combined_fn = pair_h_and_ha(heuristic_fn, successor_fn)
    generator_fn = single_generator(goal, operators, axioms, combined_fn)
    return search_fn(initial, goal, generator_fn, evaluator_fn, **kwargs)

###########################################################################

#default_successors = pair_h_and_ha(h_add, ha_applicable)
#default_successors = pair_h_and_ha(h_ff_add, ha_applicable)
default_successors = ff_fn(plan_cost, first_goals, op=sum)

#default_search = lambda initial, goal, generator: a_star_search(initial, goal, generator, astar, stack=True)
#default_search = lambda initial, goal, generator: best_first_search(initial, goal, generator, greedy, stack=True)
default_search = lambda initial, goal, generator: best_first_search(
    initial, goal, generator, greedy, stack=False, lazy=True) # stack=True vs False can matter quite a bit

def default_plan(initial, goal, operators, axioms=[]):
    #return default_search(initial, goal, single_generator(goal, operators, axioms, default_successors))
    return solve_strips(initial, goal, operators, axioms=axioms)

default_derived_plan = default_plan
