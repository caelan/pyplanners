from .ff import ff_fn, plan_cost, first_goals
from misc.numerical import INF
from misc.functions import in_add
from planner.progression.best_first import a_star_search, best_first_search, deferred_best_first_search

def h_0(state, goal, operators):
    return 0
def h_naive(state, goal, operators):
    return sum(1 for literal in goal.conditions if literal not in state)
def h_blind(state, goal, operators):
    return min(operator.cost for operator in ha_applicable(state, goal, operators))

###########################################################################

def filter_axioms(operators):
    return list(filter(lambda o: not o.is_axiom(), operators))

def ha_all(state, goal, operators):
    return operators
def ha_applicable(state, goal, operators):
    return [operator for operator in operators if operator(state) is not None]
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

# TODO: custom heuristic

def combine(heuristic, helpful_actions):
    return lambda s, g, o: (heuristic(s, g, o), helpful_actions(s, g, o))

#default_successors = combine(h_add, ha_applicable)
default_successors = ff_fn(plan_cost, first_goals, op=sum)

###########################################################################

def single_generator(initial, goal, operators, successors):
    def generator(vertex):
        yield successors(vertex.state, goal, operators)
    return generator
    #return = lambda v: (yield successors(v.state, goal, operators))

def filter_axioms_generator(goal, operators, axioms, successors):
    def generator(vertex):
        #heuristic, helpful_actions = successors(vertex.state, goal, operators + axioms)
        heuristic, helpful_actions = successors(vertex.derived_state, goal, operators + axioms)
        #yield heuristic, helpful_actions
        #yield heuristic, operators
        yield heuristic, filter_axioms(helpful_actions) # NOTE - the first_actions should be anything applicable in derived_state
        #yield heuristic, filter(lambda op: op not in axioms, helpful_actions)
    return generator, axioms

default_generator = lambda i, g, o: single_generator(i, g, o, default_successors)

###########################################################################

def weighted(w):
    if w == INF:
        return lambda v: v.h_cost
    return lambda v: (v.cost + w*v.h_cost)

uniform = weighted(0)
astar = weighted(1)
greedy = weighted(INF)

###########################################################################

# TODO: # stack=True vs False can matter quite a bit
#default_search = lambda initial, goal, generator: a_star_search(initial, goal, generator, astar, stack=True)
default_search = lambda initial, goal, generator: best_first_search(initial, goal, generator, greedy, stack=True)
#default_search = lambda initial, goal, generator: deferred_best_first_search(initial, goal, generator, greedy, stack=True)

def default_plan(initial, goal, operators):
    return default_search(initial, goal, default_generator(initial, goal, operators))

def default_derived_plan(initial, goal, operators, axioms):
    #return default_search(initial, goal, (lambda v: iter([default_successors(v.state, goal, operators + axioms)]), axioms))
    return default_search(initial, goal, filter_axioms_generator(goal, operators, axioms, default_successors))
