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
    parent_op = parent_edge.operator
    if not hasattr(parent_op, 'test'):
        return True
    parent_state = parent_edge.source.state
    # TODO: apply external functions
    if parent_op.test(parent_state):
        return True
    parent_edge.cost = INF
    sink_vertex.reset_path()
    return False

def order_successors(successors, stack=False):
    return reversed(successors) if stack else successors

###########################################################################

def a_star_search(start, goal, generator, priority, stack=False,
                  max_time=INF, max_iterations=INF, debug=None, **kwargs):
    # TODO: update to use test_parent_operator
    state_space = StateSpace(generator, start, max_extensions=INF, **kwargs)
    sv = state_space.root
    if sv.contained(goal):
        return state_space.solution(sv)
    if not sv.generate():
        return state_space.failure()
    queue = (FILOClassicPriorityQueue if stack else FIFOClassicPriorityQueue)([(priority(sv), sv)])
    while not queue.empty() and (elapsed_time(state_space.start_time) < max_time) \
            and (state_space.iterations < max_iterations):
        cv = queue.pop()
        state_space.iterations += 1
        if debug is not None:
            debug(cv)
        if test_goal(cv, goal):
            return state_space.solution(cv)
        cv.generate_all() # NOTE - A* is not optimal even for an admissible heuristic if you allow re-expansion of branches
        if cv.h_cost is None:
            continue
        for nv in order_successors(cv.unexplored(), stack):
            if nv.generate():
                queue.decrease_key(priority(nv), nv)
    return state_space.failure()

def best_first_search(start, goal, generator, priority, stack=False, lazy=True,
                      max_time=INF, max_iterations=INF, debug=None, **kwargs):
    state_space = StateSpace(generator, start, max_extensions=INF, **kwargs) # TODO: max_extensions=1 can fail when test
    sv = state_space.root
    sv.generate()
    if sv.is_dead_end(): # tests for an infinite (safe) heuristic value
        return state_space.failure()
    queue = (FILOPriorityQueue if stack else FIFOPriorityQueue)([(priority(sv), sv)])
    while not queue.empty() and (elapsed_time(state_space.start_time) < max_time) \
            and (state_space.iterations < max_iterations):
        state_space.iterations += 1
        cv = queue.pop()
        if lazy and not test_parent_operator(cv):
            continue
        if debug is not None: # TODO: make a cleaner function for this
            debug(cv)
        if test_goal(cv, goal):
            return state_space.solution(cv)
        successors = list(cv.unexplored())
        if not cv.enumerated():
            successors.append(cv)
        for nv in order_successors(successors, stack):
            nv.generate() # Also evaluates the h_cost
            if (not nv.is_dead_end()) and (lazy or test_parent_operator(nv)):
                queue.push(priority(nv), nv)
    return state_space.failure()

def deferred_best_first_search(start, goal, generator, priority, stack=False,
                               max_time=INF, max_iterations=INF, debug=None, **kwargs):
    state_space = StateSpace(generator, start, max_extensions=INF, **kwargs) # TODO: max_extensions=1 can fail when test
    queue = (FILOPriorityQueue if stack else FIFOPriorityQueue)([(None, state_space.root)])
    while not queue.empty() and (elapsed_time(state_space.start_time) < max_time) \
            and (state_space.iterations < max_iterations):
        state_space.iterations += 1
        cv = queue.pop()
        cv.generate()
        if cv.is_dead_end():
            continue
        if not test_parent_operator(cv): # always lazy
            continue
        if debug is not None:
            debug(cv)
        if test_goal(cv, goal):
            return state_space.solution(cv)
        successors = list(cv.unexplored())
        if not cv.enumerated():
            successors.append(cv) # TODO: use its prior value
        for nv in order_successors(successors, stack):
            # TODO: incorporate the path cost of nv instead of cv
            queue.push(priority(cv), nv)
    return state_space.failure()
