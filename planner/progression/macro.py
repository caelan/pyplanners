from misc.functions import elapsed_time, first
from misc.numerical import INF
from misc.priority_queue import FILOPriorityQueue, FIFOPriorityQueue
from planner.progression.best_first import order_successors
from planner.state_space import StateSpace


def macro_greedy_cost_fn(v):
    # TODO: only want to perform this if the macro is helpful
    if v.parent_edge is None:
        return v.h_cost
    return v.parent_edge.source.h_cost - len(v.parent_edge.operator)


def macro_deferred_best_first_search(start, goal, generator, priority, stack=False, debug=None, **kwargs):
    space = StateSpace(generator, start, max_extensions=1, **kwargs)
    sv = space.root
    if sv.contained(goal):
        return space.solution(sv)
    queue = (FILOPriorityQueue if stack else FIFOPriorityQueue)([(None, sv)])
    while not queue.empty() and space.is_active():
        cv = queue.pop()
        if not cv.generate():
            continue
        space.iterations += 1
        if debug is not None:
            debug(cv)
        successors = list(cv.unexplored()) + [cv]
        gv = first(lambda v: v.contained(goal), successors[:-1])
        if gv is not None:
            return space.solution(gv)
        for nv in order_successors(successors, stack):
            queue.push(priority(nv), nv)
    return space.failure()
