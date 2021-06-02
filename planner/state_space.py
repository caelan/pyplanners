from collections import namedtuple

from .operators import derive_predicates, MacroOperator
from misc.functions import elapsed_time, safe_remove, implies
from misc.numerical import INF
from misc.objects import str_line
import time

# TODO - can rewire state-space if found a better parent

IS_SAFE = True # http://www.fast-downward.org/Doc/Evaluator

Solution = namedtuple('Solution', ['plan', 'state_space'])
Priority = namedtuple('Priority', ['cost', 'length'])

class Plan(object):
    def __init__(self, start, operators):
        self.start = start
        self.operators = operators
    @property
    def cost(self):
        if not self.operators:
            return 0
        return sum(operator.cost for operator in self.operators)
    @property
    def length(self):
        return len(self.operators)
    @property
    def priority(self):
        return Priority(self.cost, self.length)
    def __iter__(self):
        return iter(self.operators)
    def get_states(self):
        states = [self.start]
        for operator in self.operators:
            #assert states[-1] in operator
            #states.append(operator(states[-1]))
            states.append(operator.apply(states[-1]))
        return states
    def get_derived_states(self, axioms):
        states = [self.start]
        derived_state, axiom_plan = derive_predicates(states[-1], axioms)
        derived_states = [derived_state]
        axiom_plans = [axiom_plan]
        for operator in self.operators:
            assert derived_states[-1] in operator
            states.append(operator.apply(states[-1]))
            derived_state, axiom_plan = derive_predicates(states[-1], axioms)
            derived_states.append(derived_state)
            axiom_plans.append(axiom_plan)
        return derived_states, axiom_plans
    def __str__(self):
        s = '{name} | Cost: {self.cost} | Length {self.length}'.format(name=self.__class__.__name__, self=self)
        for i, operator in enumerate(self.operators):
            s += str_line('\n%d | '%(i+1), operator)
        return s
    __repr__ = __str__

#################################################################

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

class Vertex(object):
    def __init__(self, state, state_space):
        self.state = state
        self.derived_state, self.axiom_plan = derive_predicates(state, state_space.axioms)
        self.state_space = state_space
        self.generator = state_space.generator_fn(self)
        self.operators = []
        self.incoming_edges = []
        self.outgoing_edges = []
        self.extensions = 0 # TODO: deprecate
        self.generations = 0
        self.explored = 0
        self.h_cost = None
        self.reset_path()
    # @property
    # def extensions(self):
    #     return len(self.outgoing_edges)
    @property
    def num_unexplored(self):
        #return self.extensions - self.explored
        return len(self.outgoing_edges) - self.explored
    def reset_path(self):
        self.cost = INF # TODO: path_cost
        self.length = INF # TODO: path_length
        self.parent_edge = None
        for edge in self.incoming_edges:
            self.relax(edge)
        for child in self.get_children():
            child.reset_path()
    # @property
    # def cost(self):
    #      if self.parent_edge is None:
    #          return 0
    #      return self.parent_edge.path_cost
    @property
    def priority(self):
        return Priority(self.cost, self.length)
    def relax(self, edge):
        assert edge.sink == self
        if edge.priority < self.priority:
            self.cost, self.length = edge.priority
            self.parent_edge = edge
            return True
        return False
    def get_children(self):
        return [edge.sink for edge in self.outgoing_edges if edge.is_parent()]
    def contained(self, partial_state):
        #return self.state in partial_state
        return self.derived_state in partial_state
    def enumerated(self):
        return (self.generator is None) or (self.state_space.max_generations <= self.generations)
    def get_h_cost(self):
        if self.h_cost is None:
            self.generate_all()
        return self.h_cost
    def get_successors(self):
        self.generate_all()
        return self.outgoing_edges
    def is_dead_end(self):
        # assumes the heuristic is safe
        assert self.h_cost is not None # TODO: call h_cost if haven't done so far
        h = self.h_cost[0] if isinstance(self.h_cost, tuple) else self.h_cost
        return IS_SAFE and (h == INF)
    def evaluate(self):
        if self.enumerated():
            return False  # TODO: change the semantics of this to be generated at least one new
        try:
            self.h_cost, operators = next(self.generator)
        except StopIteration:
            self.generator = None
            return False
        if (self.state_space.best_h is None) or (self.h_cost < self.state_space.best_h):
            self.state_space.best_h = self.h_cost
            self.state_space.dump()
        self.operators.extend(operators)
        if self.generations == 0:
            self.state_space.num_expanded += 1
        self.state_space.num_generations += 1
        self.generations += 1
        return True
    def extend_state_space(self):
        operators = list(self.operators)
        self.operators = []
        if self.is_dead_end():
            return []
        for operator in operators:  # TODO - should states be expanded before the heuristic check?
            self.state_space.extend(self, operator)
        return operators  # TODO - decide if to return true if still some unexplored (despite nothing new generated)
    def generate(self):
        if not self.evaluate():
            return False
        return bool(self.extend_state_space())
    def generate_all(self):
        new = False
        while not self.enumerated():
            new |= self.generate()
        return new
    def has_unexplored(self):
        return self.num_unexplored > 0
    def unexplored(self):
        self.extend_state_space()
        while self.has_unexplored():
            self.explored += 1
            yield self.outgoing_edges[self.explored-1].sink
    def dump(self):
        print('h_cost: {self.h_cost} | cost: {self.cost} | length: {self.length} | '
              'generations: {self.generations} | unexplored: {unexplored}\n{self.state}'.format(
            self=self, unexplored=self.num_unexplored))
    def __str__(self):
        #return '{}({})'.format(self.__class__.__name__, id(self))
        return '{}({})'.format(self.__class__.__name__, self.state)
    __repr__ = __str__

class Edge(object):
    def __init__(self, source, sink, operator, state_space):
        self.source = source
        self.sink = sink # TODO: lazily evaluate the next state
        self.operator = operator
        self.state_space = state_space
        self.cost = self.operator.cost # TODO: attachments cost function
        self.source.outgoing_edges.append(self)
        self.sink.incoming_edges.append(self)
        self.sink.relax(self)
        self.valid = None if hasattr(operator, 'test') else True
    @property
    def path_cost(self):
        return self.source.cost + self.cost
    @property
    def path_length(self):
        return self.source.length + 1
    @property
    def priority(self):
        return Priority(self.path_cost, self.path_length)
    def is_parent(self): # TODO: what was the purpose of this?
        return self.sink.parent_edge == self
    # def delete(self):
    #     safe_remove(self.source.outgoing_edges, self)
    #     safe_remove(self.sink.incoming_edges, self)
    #     safe_remove(self.state_space.edges, self)
    #     if self.is_parent():
    #         # TODO: propagate
    #         self.sink.reset_path()
    def evaluate_test(self):
        if self.valid is None:
            # TODO: apply external functions
            self.valid = bool(self.operator.test(self.source.state))
            if not self.valid:
                self.cost = INF
                self.sink.reset_path()
        return self.valid
    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.operator)
    __repr__ = __str__

#################################################################

class StateSpace(object):
    def __init__(self, generator_fn, start, max_extensions=INF, max_generations=INF, max_cost=INF, max_length=INF,
                 max_time=INF, max_iterations=INF, verbose=True, dump_rate=1.): # 0 | 1 | INF
        # TODO: move queue here?
        self.start_time = time.time()
        self.iterations = 0
        self.num_expanded = 0
        self.num_generations = 0
        self.vertices = {}
        self.edges = [] # NOTE - allowing parallel-edges
        #self.solutions = []
        if isinstance(generator_fn, tuple): # TODO - fix this by making the operators a direct argument
            self.generator_fn, self.axioms = generator_fn
        else:
            self.generator_fn, self.axioms = generator_fn, []
        # TODO: could check whether these are violated generically
        self.max_extensions = max_extensions
        self.max_generations = max_generations
        self.max_cost = max_cost
        self.max_length = max_length
        self.max_time = max_time
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.dump_rate = dump_rate
        self.last_dump = time.time()
        self.root = self[start]
        self.root.cost = 0
        self.root.length = 0
        self.root.extensions += 1
        self.best_h = None # None | INF
    def has_state(self, state):
        return state in self.vertices
    __contains__ = has_state
    def get_state(self, state):
        if state not in self:
            self.vertices[state] = Vertex(state, self)
        return self.vertices[state]
    __getitem__ = get_state
    def __iter__(self):
        return iter(self.vertices.values())
    def __len__(self):
        return len(self.vertices)
    def new_iteration(self, vertex):
        self.iterations += 1
        if elapsed_time(self.last_dump) >= self.dump_rate:
            self.dump()
        # TODO: record dead ends here
        #return vertex.is_dead_end() # TODO: might not have called h_cost
    def is_active(self):
        return (elapsed_time(self.start_time) < self.max_time) or (self.iterations < self.max_iterations)
    def extend(self, vertex, operator):
        if (vertex.cost + operator.cost <= self.max_cost) \
                and (vertex.length + len(operator) <= self.max_length) \
                and vertex.contained(operator):
            #if vertex.state in operator:
            if self.axioms:
                assert not isinstance(operator, MacroOperator)
                sink_state = operator.apply(vertex.state) # TODO - this won't work for MacroOperators yet?
            else:
                sink_state = operator(vertex.state)[-1] if isinstance(operator, MacroOperator) else operator(vertex.state)
            if (sink_state is not None) and (self[sink_state].extensions < self.max_extensions):
                sink_vertex = self[sink_state]
                self.edges.append(Edge(vertex, sink_vertex, operator, self))
                sink_vertex.extensions += 1
                return sink_vertex
        return None
    def retrace(self, vertex):
        if vertex is not None:
            if vertex == self.root:
                return []
            sequence = self.retrace(vertex.parent_edge.source)
            if sequence is not None:
                return sequence + list(vertex.parent_edge.operator)
        return None
    def plan(self, vertex):
        sequence = self.retrace(vertex)
        if sequence is None:
            return None
        return Plan(self.root.state, sequence)
    def solution(self, vertex):
        #self.dump()
        return Solution(self.plan(vertex), self)
    def failure(self):
        self.dump()
        return Solution(None, self)
    def time_elapsed(self):
        return elapsed_time(self.start_time)
    def __repr__(self):
     # TODO: deadends, backtracking, expanded/generated until last jump, etc.
        return 'Iterations: {iterations} | State Space: {state_space} | Expanded: {expanded} | ' \
               'Generations: {generations} | Heuristic: {heuristic} | Time: {time:.3f}'.format(
            iterations=self.iterations, state_space=len(self), expanded=self.num_expanded,
            generations=self.num_generations, heuristic=self.best_h, time=self.time_elapsed())
    def dump(self):
        if not self.verbose:
            return
        self.last_dump = time.time()
        print(self)
        # TODO: record iterations since last heuristic
