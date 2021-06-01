import random

from planner.state_space import test_goal, test_parent_operator, StateSpace, Solution, Plan
from misc.numerical import INF
from misc.priority_queue import FIFOClassicPriorityQueue, FILOClassicPriorityQueue, FIFOPriorityQueue, FILOPriorityQueue


def random_policy(current_vertex):
    current_vertex.generate_all()
    if not current_vertex.outgoing_edges:
        return None # current_vertex
    edge = random.choice(current_vertex.outgoing_edges)
    return edge

def random_walk(start, goal, generator, _=None, debug=None, **kwargs):
    space = StateSpace(generator, start, max_extensions=INF, **kwargs)
    current_vertex = space.root
    edge_path = []
    while space.is_active():
        space.new_iteration(current_vertex)
        if debug is not None:
            debug(current_vertex)
        if test_goal(current_vertex, goal):
            operator_path = [edge.operator for edge in edge_path]
            plan = Plan(start, operator_path)
            return Solution(plan, space)
            #return space.solution(current_vertex)
        edge = random_policy(current_vertex)
        if edge is None:
            break
        edge_path.append(edge)
        current_vertex = edge.sink
    return space.failure()

def mcts(start, goal, generator, priority, stack=False, lazy=True, debug=None, **kwargs):
    # TODO: dynamic programming
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
