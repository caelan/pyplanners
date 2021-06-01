from ..state_space import StateSpace
from misc.numerical import INF
from misc.functions import reverse, elapsed_time
from misc.priority_queue import FIFOClassicPriorityQueue, FILOClassicPriorityQueue, FIFOPriorityQueue, FILOPriorityQueue

# TODO - Update the shortest path using Bellman-Ford if find shorter path to previously visited state
# NOTE - Best first searches with infinite branching factors are not complete. Need to use iterative deepening on max_expansions and max_length

def weighted(weight):
    # TODO: could recover the parent's heuristic value for deferred evaluation
    if weight == INF:
        return lambda v: v.h_cost
    return lambda v: v.cost + weight * v.h_cost

uniform = weighted(0)
astar = weighted(1)
wastar2 = weighted(2)
wastar3 = weighted(2)
greedy = weighted(INF)
lexicographic = lambda v: (v.h_cost, v.cost)

###########################################################################

def test_goal(vertex, goal):
    if not vertex.contained(goal):
        return False
    if not hasattr(goal, 'test'):
        return True
    return goal.test(vertex.state)

def test_parent_operator(sink_vertex):
    parent_edge = sink_vertex.parent_edge
    if parent_edge is None:
        return True
    return parent_edge.evaluate_test()

def order_successors(successors, stack=False):
    return reversed(successors) if stack else successors

###########################################################################

def a_star_search(start, goal, generator, priority, stack=False, debug=None, **kwargs):
    # TODO: lazy a_star
    # TODO: update to use test_parent_operator
    space = StateSpace(generator, start, max_extensions=INF, **kwargs)
    sv = space.root
    if sv.contained(goal):
        return space.solution(sv)
    if not sv.generate():
        return space.failure()
    queue = (FILOClassicPriorityQueue if stack else FIFOClassicPriorityQueue)([(priority(sv), sv)])
    while not queue.empty() and space.is_active():
        cv = queue.pop()
        space.new_iteration(cv)
        if debug is not None:
            debug(cv)
        if test_goal(cv, goal):
            return space.solution(cv)
        cv.generate_all() # NOTE - A* is not optimal even for an admissible heuristic if you allow re-expansion of branches
        if cv.h_cost is None:
            continue
        for nv in order_successors(cv.unexplored(), stack):
            if nv.generate():
                queue.decrease_key(priority(nv), nv)
    return space.failure()

def best_first_search(start, goal, generator, priority, stack=False, lazy=True, debug=None, **kwargs):
    # TODO: anytime mode
    space = StateSpace(generator, start, max_extensions=INF, **kwargs) # TODO: max_extensions=1 can fail when test
    sv = space.root
    sv.generate()
    if sv.is_dead_end(): # tests for an infinite (safe) heuristic value
        return space.failure()
    queue = (FILOPriorityQueue if stack else FIFOPriorityQueue)([(priority(sv), sv)])
    while not queue.empty() and space.is_active():
        cv = queue.pop()
        space.new_iteration(cv)
        if lazy and not test_parent_operator(cv):
            continue
        if debug is not None: # TODO: make a cleaner function for this
            debug(cv)
        if test_goal(cv, goal):
            return space.solution(cv)
        successors = list(cv.unexplored())
        if not cv.enumerated():
            successors.append(cv)
        for nv in order_successors(successors, stack):
            nv.evaluate() # nv.generate() # Also evaluates the h_cost
            if (not nv.is_dead_end()) and (lazy or test_parent_operator(nv)):
                queue.push(priority(nv), nv)
    return space.failure()

def deferred_best_first_search(start, goal, generator, priority, stack=False, debug=None, **kwargs):
    space = StateSpace(generator, start, max_extensions=INF, **kwargs) # TODO: max_extensions=1 can fail when test
    queue = (FILOPriorityQueue if stack else FIFOPriorityQueue)([(None, space.root)])
    while not queue.empty() and space.is_active():
        cv = queue.pop()
        cv.evaluate() # cv.generate()
        space.new_iteration(cv)
        if cv.is_dead_end():
            continue
        if not test_parent_operator(cv): # always lazy
            continue
        if debug is not None:
            debug(cv)
        if test_goal(cv, goal):
            return space.solution(cv)
        successors = list(cv.unexplored())
        if not cv.enumerated():
            successors.append(cv) # TODO: use its prior value
        for nv in order_successors(successors, stack):
            # TODO: incorporate the path cost of nv instead of cv
            queue.push(priority(cv), nv)
    return space.failure()
