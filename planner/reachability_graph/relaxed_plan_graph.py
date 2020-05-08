from reachability_graph import *
from misc.utils import *

# TODO
# - make the levels based on subproblem switches (use problem_reachable_sources). Don't count things moved by the same controller
# - flag to terminate costs/levels when the goals are reached (sometimes wouldn't want that though?)
# - support dynamically updating costs. Currently, my compute_costs/levels method assumes costs are INF
# - move these to another file to compute the costs generically?
# - cost per instance of the variable returned as a function of each independent problem?

# TODO
# - active edge stuff
# Could include reachability checks that don't propagate to things that go through the goal (but what's really the point)

# TODO - call delete-relaxation graph
# Make related plan graph extend delete relation graph
# Incorporate set-additive

class RelaxedPlanGraph(ReachabilityGraph):

  # Need call this when the goal starts to open problems on the queue
  # Start opening problems for actions as soon as they have all intermediates reachable
  # Just the connected parts of the connector to do opening of problem when solving things and stuff

  # TODO - Mark attempted edges to discount for growing stuff
  def grow(self, max_time=INF, max_iterations=INF, max_cycles=INF, greedy=True):
    if max_time == INF and max_iterations == INF and max_cycles == INF and not greedy:
      raise RuntimeError('RelaxedPlanGraph.grow() will never terminate')
    if self.exhausted:
      return

    # Total time, total iterations, cycles, ...
    start_time, iterations, cycles = time(), 0, 0
    self.greedy = greedy
    self.queue = deque([None]) # Reuse same queue each time?

    self.start.set_reachable()
    self.goal.set_active()

    while time() - start_time <= max_time and iterations <= max_iterations and cycles <= max_cycles:
      if self.greedy and self.goal.reachable: break

      subplanner = self.queue.popleft()
      if subplanner is None: # Dummy node to count the number of cycles
        cycles += 1
        if len(self.queue) == 0: break
        self.queue.append(None)
        continue
      subplanner.queued = False
      if not subplanner.goal_connector.active: continue
      iterations += 1 # Iterations of planner processing

      subplanner()
      if subplanner.exhausted:
        # TODO - something special if the problem is exhausted
        continue
      if subplanner.goal_connector.active and not subplanner.queued:
        self.queue.append(subplanner); subplanner.queued = True

    self.reachable, self.exhausted = self.goal.reachable, len(self.queue) == 0
    self.total_time += time() - start_time; self.total_iterations += iterations; self.total_cycles += cycles

    """
    # TODO - a couple random nodes are still active despite attempts
    for n in (self.vertices.values() + self.edges.values() + self.connectors.values()):
      if n.active:
        print n
    print sum(1 for n in (self.vertices.values() + self.edges.values() + self.connectors.values()) if not n.active)
    print sum(1 for n in (self.vertices.values() + self.edges.values() + self.connectors.values()) if n.active)
    print len(self.vertices.values() + self.edges.values() + self.connectors.values())
    print self.goal.active
    """
    #self.graph('test.pdf', reachable=False)
    #raw_input()

  ###########################################################################

  # TODO - costs dependent on mode switches
  def costs(self, op=max, unit=False, greedy=True):
    self.op, self.unit = op, unit

    for node in self.vertices.values() + self.edges.values() + self.connectors.values():
      node.cost = INF; node.level = INF
    for edge in self.edges.values():
      edge.num_finite_cost = 0

    self.start.cost, self.start.level = 0, 0
    queue = [(0, self.start)]
    processed = set()
    while len(queue) != 0:
      _, vertex = heappop(queue)
      if vertex in processed: continue
      processed.add(vertex)

      for sink_vertex, edge in vertex.sinks: # Sink Vertex
       if edge.cost == INF: continue
       new_cost = op(vertex.cost, edge.cost) + (edge.value.cost if not unit else 1)
       if new_cost < edge.cost:
         sink_vertex.cost, sink_vertex.level = new_cost, max(vertex.level, edge.level) + 1
         heappush(queue, (sink_vertex.cost, sink_vertex))

      for connector in vertex.connectors: # Connector
        if connector.cost == INF:
          connector.cost, connector.level = vertex.cost, vertex.level
          for edge in connector.edges: # Edge
            edge.num_finite_cost += 1
            if edge.num_finite_cost == len(edge.value.conditions):
              edge.cost, edge.level = op(c.cost for c in edge.connectors), max(c.level for c in edge.connectors)
              if greedy and edge == self.goal: return
              for source_vertex, sink_vertex in edge.mappings: # Vertex
                source_cost, source_level = edge.cost, edge.level
                if source_vertex is not None:
                  if source_vertex not in processed: continue
                  source_cost, source_level = op(source_cost, source_vertex.cost), max(source_vertex.level, source_level)

                new_cost = source_cost + (edge.value.cost if not unit else 1)
                if new_cost < sink_vertex.cost:
                  sink_vertex.cost, sink_vertex.level = new_cost, source_level + 1
                  heappush(queue, (sink_vertex.cost, sink_vertex))

  ###########################################################################

  #def direct_vertex_achievers(self, vertex, l_fn):
  #  return filter(lambda (v, e): l_fn(e) == l_fn(vertex)-1 and (v is None or l_fn(v)==l_fn(vertex)-1), vertex.sources) # TODO - fix

  def all_vertex_achievers(self, vertex, l_fn):
    return list(filter(lambda item: l_fn(item[1]) < l_fn(vertex) and (item[0] is None or l_fn(item[0]) < l_fn(vertex)), vertex.sources))
  def all_connector_achievers(self, connector, l_fn):
    return list(filter(lambda v: l_fn(v) <= l_fn(connector), connector.vertices))

  def discounted_vertex_cost(self, vertex, l_fn, h_fn):
    if vertex in self.relaxed_plan_vertices[l_fn(vertex)]: return 0
    return h_fn(vertex)
  def discounted_edge_cost(self, edge, l_fn, h_fn, op=sum): # TODO - get rid of op
    return op(min(self.discounted_vertex_cost(v, l_fn, h_fn) for v in self.all_connector_achievers(c, l_fn)) for c in edge.connectors)

  def easiest_edge(self, vertex, l_fn, h_fn): # TODO - factor in v when computing the cost and level
    return argmin(lambda item: self.discounted_edge_cost(item[1], l_fn, h_fn), self.all_vertex_achievers(vertex, l_fn))
  def easiest_vertex(self, connector, l_fn, h_fn):
    return argmin(lambda v: self.discounted_vertex_cost(v, l_fn, h_fn), self.all_connector_achievers(connector, l_fn))

  def random_layer(self, layer): return randomize(layer)
  def easy_layer(self, layer, h_fn): return sorted(layer, key=h_fn)

  def linearize_plan(self, l_fn=lambda n: n.level, h_fn=lambda n: n.cost):
    self.relaxed_plan_vertices = [set() for _ in range(l_fn(self.goal) + 1)]
    self.relaxed_plan_edges = [set() for _ in range(l_fn(self.goal))]
    for new_vertex in (self.easiest_vertex(c, l_fn, h_fn) for c in self.goal.connectors):
      self.relaxed_plan_vertices[l_fn(new_vertex)].add(new_vertex)

    marked_vertices = [set() for _ in range(l_fn(self.goal) + 1)]
    for level in reversed(range(1, len(self.relaxed_plan_vertices))):
      for vertex in self.easy_layer(self.relaxed_plan_vertices[level] - marked_vertices[level], h_fn):
        source, edge = self.easiest_edge(vertex, l_fn, h_fn)
        self.relaxed_plan_edges[l_fn(edge)].add(edge)
        for new_vertex in [self.easiest_vertex(c, l_fn, h_fn) for c in edge.connectors] + ([source] if source is not None else []):
          if new_vertex not in marked_vertices[level-1]:
            self.relaxed_plan_vertices[l_fn(new_vertex)].add(new_vertex)
        for _, sink_vertex in edge.mappings:
          marked_vertices[level].add(sink_vertex)
          marked_vertices[level-1].add(sink_vertex) # Assumes that actions are sequenced in the order they are selected

  ###########################################################################

  def graph_rpg(self, filename, reachable=True):
    from pygraphviz import AGraph # NOTE - LIS machines do not have pygraphviz
    graph = AGraph(strict=True, directed=True)

    for vertex in self.vertices.values():
      for connector in vertex.connectors:
        if vertex.level <= connector.level and (not reachable or (vertex.reachable and connector.reachable)):
          graphviz_connect(graph, vertex, connector)
    for connector in self.connectors.values():
      for edge in connector.edges:
        if connector.level <= edge.level and (not reachable or (connector.reachable and edge.reachable)):
          graphviz_connect(graph, connector, edge)
    for edge in self.edges.values():
      for _, sink_vertex in edge.mappings:
        if edge.level <= sink_vertex.level and (not reachable or (edge.reachable and sink_vertex.reachable)):
          graphviz_connect(graph, edge, sink_vertex)

    graph.draw(filename, prog='dot')

  def str_rpg(self):
    vertex_levels = defaultdict(set)
    for vertex in self.vertices.values():
      vertex_levels[vertex.level].add(vertex)

    connector_levels = defaultdict(set)
    for connector in self.connectors.values():
      connector_levels[connector.level].add(connector)

    edge_levels = defaultdict(set)
    for edge in self.edges.values():
      edge_levels[edge.level].add(edge)

    s = self.__class__.__name__
    for level in sorted(set(vertex_levels.keys() + connector_levels.keys() + edge_levels.keys())):
      s += '\n\n---Level ' + str(level) + '---\n' + \
        'Vertices: ' + str_object(vertex_levels.get(level, [])) + '\n' + \
        'Connectors: ' + str_object(connector_levels.get(level, [])) + '\n' + \
        'Edges: ' + str_object(edge_levels.get(level, []))
    return s
