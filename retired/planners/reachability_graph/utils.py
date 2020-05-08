# TODO - For a context-enhanced graph, pair vertex, connector, and edge with the context state it is reached from

REACHABLE_EXPAND = True # TODO - similar in function greedy?
INACTIVE = False # TODO - turned this off because don't need it with one generation
INITIAL_GENERATION = False

def graphviz_connect(graph, item1, item2):
  graph.add_node(item1.node_str())
  node1 = graph.get_node(item1.node_str())
  node1.attr.update(item1.node_attr())
  graph.add_node(item2.node_str())
  node2 = graph.get_node(item2.node_str())
  node2.attr.update(item2.node_attr())
  graph.add_edge(node1, node2)
