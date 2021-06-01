from collections import deque

from ..state_space import StateSpace
from ..operators import MacroOperator
from misc.utils import in_add, chain
from misc.objects import enum
from misc.numerical import INF

# TODO
# - Optimal variant that finds 1 or more plans, and WPS off those paths to find a low cost path
# - Decide how much to reuse past WPS structure in each iteration of the hill climbing. On one hand
#   I already have a lot of branches created when I reuse the start. On the other, it would disproportionately
#   take up more time over the search from the current best state
# - Use RBFS as a primitive search operation and pass the state_space
# - Use best first search as local search along with the other heuristic values
# - Maintain the hill climbing queue

strategies = enum('LOCAL', 'REVERSE', 'START', 'SEQUENCE')


def hill_climbing_search(start, goal, generator, _, cost_step=1, strategy=strategies.LOCAL, recurrence=1, steepest=True,
                         debug=INF, **kwargs):
    space = StateSpace(generator, start, INF, **kwargs)  # NOTE - max_extensions needs to be INF

    def negative_gradient(cost1, cost2):
        if cost_step is None:
            return cost1 < cost2
        cost = cost1 if type(cost1) not in [tuple, list] else cost1[0]
        return cost not in [None, INF] and (cost <= (cost2 - cost_step))

    def local_search(vertices, h_cost):
        queue, reached = deque(), set()
        for nv in vertices:
            if not in_add(nv, reached):
                nv.pops, nv.explored = 0, 0
                if nv.h_cost is not None:
                    queue.append(nv)

        while queue and space.is_active():
            cv = queue.popleft()
            cv.pops += 1
            if (cv.pops - 1) % recurrence != 0:
                queue.append(cv)
                continue
            space.iterations += 1
            if debug is not None:
                debug(cv)

            successors = []
            for nv in cv.unexplored() if strategy is not strategies.REVERSE or cv.parent_edge is None \
                    else chain(cv.unexplored(), [cv.parent_edge.source]):  # TODO - option to chain all incoming_edges
                if not in_add(nv, reached):
                    nv.pops, nv.explored = 0, 0
                    if nv.generations == 0 and (nv.contained(goal) or (nv.generate() and not steepest
                                                                       and negative_gradient(nv.h_cost, h_cost))):
                        return nv
                    if nv.h_cost is not None:
                        successors.append(nv)

            successors = sorted(successors, key=lambda e: e.h_cost)
            if len(successors) > 0 and negative_gradient(successors[0].h_cost, h_cost):
                return successors[0]
            queue += successors

            if cv.generate():
                if negative_gradient(cv.h_cost, h_cost):
                    return cv
                if cv.h_cost is not None:
                    queue.append(cv)
        return None

    ###########################################################################

    sv = space.root
    if sv.contained(goal):
        return space.solution(sv)
    if not sv.generate():
        return space.failure()
    while space.is_active():
        if debug is not None:
            print(50 * '-', '\n')

        if strategy in [strategies.LOCAL, strategies.REVERSE]:
            vertices = [sv]
        elif strategy is strategies.START:
            vertices = [sv, space.root]
        elif strategy is strategies.SEQUENCE:
            path_operator = MacroOperator(*space.retrace(sv))
            path_sequence = path_operator(space.root.state)
            vertices = list(map(lambda s: space[s], path_sequence))[::-1]
        else:
            raise RuntimeError('Invalid strategy: %s' % strategy)

        sv = local_search(vertices, sv.h_cost)
        if sv is None:
            break
        if sv.contained(goal):
            return space.solution(sv)
    return space.failure()
