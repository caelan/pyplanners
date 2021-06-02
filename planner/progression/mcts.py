import random
import math
import numpy

from planner.state_space import test_goal, test_parent_operator, StateSpace, Solution, Plan
from misc.numerical import INF
from misc.functions import randomize

def random_policy(current_vertex):
    edges = current_vertex.get_successors()
    if not edges:
        return None # current_vertex
    return random.choice(edges)

def greedy_policy(current_vertex, weight=1, shuffle=True):
    # TODO: function that returns the policy
    # TODO: use evaluators
    edges = current_vertex.get_successors()
    if not edges:
        return None
    if shuffle:
        edges = randomize(edges)
    return min(edges, key=lambda e: e.cost + weight*e.sink.get_h_cost())

##################################################

def random_walk(start, goal, generator, _=None, policy=random_policy, max_steps=INF, debug=None, **kwargs):
    space = StateSpace(generator, start, max_extensions=INF, **kwargs)
    current_vertex = space.root
    edge_path = []
    while space.is_active() and len(edge_path) < max_steps:
        #current_vertex.generate_all()
        space.new_iteration(current_vertex)
        if debug is not None:
            debug(current_vertex)
        if test_goal(current_vertex, goal):
            operator_path = [edge.operator for edge in edge_path]
            plan = Plan(start, operator_path)
            return Solution(plan, space)
            #return space.solution(current_vertex)
        edge = policy(current_vertex)
        if edge is None:
            break
        edge_path.append(edge)
        current_vertex = edge.sink
    return space.failure()

##################################################

MAX_ROLLOUT = 100 # 100 | INF

class TreeNode(object):
    def __init__(self, vertex, parent_edge=None, parent_node=None):
        self.vertex = vertex
        self.parent_edge = parent_edge
        self.parent_node = parent_node
        self.rollouts = [] # TODO: rename to estimates?
        self.children = [] # TODO: map from edges to nodes
        if self.parent_node is not None:
            self.parent_node.children.append(self)
    def is_leaf(self):
        return not bool(self.children)
    def num_rollouts(self):
        return len(self.rollouts)
    def get_estimate(self):
        if not self.rollouts:
            return INF
        return numpy.average(self.rollouts)
    def get_uct(self, c=math.sqrt(2)):
        # https://en.wikipedia.org/wiki/Monte_Carlo_tree_search
        estimate = -self.get_estimate()
        if (self.parent_node is None) or (c == 0):
            return estimate
        diverse = math.sqrt(math.log(self.parent_node.num_rollouts()) / self.num_rollouts())
        if c == INF:
            return diverse
        return estimate + c*diverse
    def ancestors(self):
        if self.parent_node is None:
            return []
        return self.parent_node.ancestors() + [self.parent_node]
    def descendants(self):
        nodes = [self]
        for child in self.children:
            nodes.extend(child.descendants())
        return nodes
    def random_leaf(self):
        if not self.children:
            return self
        child = random.choice(self.children)
        return child.random_leaf()
    def uniform_leaf(self):
        leaves = list(filter(TreeNode.is_leaf, self.descendants()))
        return random.choice(leaves)
    def uct_leaf(self, **kwargs):
        if not self.children:
            return self
        best_child = max(self.children, key=lambda n: n.get_uct(**kwargs))
        return best_child.uct_leaf()
    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.vertex)

##################################################

def goal_rollout(vertex, goal):
    if test_goal(vertex, goal):
        return 0
    return 1 # TODO: min action cost

def deadend_rollout(vertex, goal):
    if test_goal(vertex, goal):
        return 0
    if not vertex.get_successors():
        return MAX_ROLLOUT
    return 1

def heuristic_rollout(vertex, goal):
    return vertex.get_h_cost()

def simulation(start_vertex, goal, policy=random_policy, max_steps=5):
    current_vertex = start_vertex
    path = []
    while len(path) < max_steps:
        if test_goal(current_vertex, goal):
            # TODO: greedy version
            break
        edge = policy(current_vertex)
        if edge is None:
            break
        path.append(edge)
        current_vertex = edge.sink
    return path

def simulated_rollout(vertex, goal, evaluator=deadend_rollout, **kwargs):
    path = simulation(vertex, goal, **kwargs)
    cost = 0
    estimates = [cost + evaluator(vertex, goal)]
    for edge in path:
        cost += edge.cost
        estimates.append(cost + evaluator(vertex, goal))
    return estimates[-1]
    #return numpy.average(estimates)

def simulated_rollouts(vertex, goal, num=1, **kwargs):
    assert num >= 1
    return numpy.average([simulated_rollout(vertex, goal, **kwargs) for _ in range(num)])

##################################################

def mcts(start, goal, generator, _=None, debug=None, **kwargs):
    # TODO: dynamic programming instead of independent tree
    # https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1
    # https://github.com/pbsinclair42/MCTS/blob/master/mcts.py
    # https://github.com/int8/monte-carlo-tree-search/blob/master/mctspy/tree/search.py
    space = StateSpace(generator, start, max_extensions=INF, **kwargs)
    root = TreeNode(space.root)
    while space.is_active():
        #leaf = root.uniform_leaf()
        #leaf = root.random_leaf()
        leaf = root.uct_leaf()
        vertex = leaf.vertex
        space.new_iteration(vertex)
        if debug is not None:
            debug(vertex)
        if test_goal(vertex, goal):
            return space.solution(vertex)
        for edge in vertex.get_successors(): # TODO: sample a subset
            new_vertex = edge.sink
            if test_goal(new_vertex, goal):
                return space.solution(new_vertex)
            node = TreeNode(new_vertex, parent_edge=edge, parent_node=leaf)
            #rollout = goal_rollout(new_vertex, goal)
            #rollout = deadend_rollout(new_vertex, goal)
            #rollout = heuristic_rollout(new_vertex, goal)
            #rollout = simulated_rollout(new_vertex, goal)
            rollout = simulated_rollouts(new_vertex, goal, num=3)
            for ancestor in reversed(node.ancestors() + [node]):
                ancestor.rollouts.append(rollout)
                if ancestor.parent_edge is not None:
                    rollout += ancestor.parent_edge.cost
    return space.failure()
