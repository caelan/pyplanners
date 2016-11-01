# TODO - For a context-enhanced graph, pair vertex, connector, and edge with the context state it is reached from

DELAYED_ACTIVATION = False

PRUNE_INACTIVE = False
CYCLE_INACTIVE = PRUNE_INACTIVE
UPDATE_INACTIVE = False

INITIAL_GENERATION = True
INTERMEDIATES_FIRST = False

def graphviz_connect(graph, item1, item2):
  graph.add_node(item1.node_str())
  node1 = graph.get_node(item1.node_str())
  node1.attr.update(item1.node_attr())
  graph.add_node(item2.node_str())
  node2 = graph.get_node(item2.node_str())
  node2.attr.update(item2.node_attr())
  graph.add_edge(node1, node2)
