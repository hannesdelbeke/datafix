from pac_sample import nodes
from pac2 import Node, ProcessNode



# register pac modules / nodes / folder
my_nodes = Node.nodes_from_module(nodes)

# todo now load a config

# todo run all nodes that are collectors
pac2.manager.collect()  # runs collection on all registered modules
pac2.manager.validate()  # runs validation on all registered modules
