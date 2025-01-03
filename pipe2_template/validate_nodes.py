from pac2 import ProcessNode, Node, ValidatorNode

# collect validations
validate_nodes = list(
    ProcessNode.iter_nodes_from_submodules(pac2.validators.deepnest)
)  # val node 1 - validation actions
print(validate_nodes)

# collect instances
strings = ["hello", "world", "hella", "hello"]
data_nodes = [Node(s) for s in strings]
print(data_nodes)

# node = DataNode(strings)  # todo good sample for adapter pattern

val_node = ValidatorNode(
    input_nodes=data_nodes, validation_node=validate_nodes[0]
)  # val node 2 - validation hookup
val_node.eval()

print(val_node)
print(val_node.results)
print(val_node.linked_nodes[0].linked_nodes)
