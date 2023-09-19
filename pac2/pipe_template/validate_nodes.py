from pac2 import ProcessNode, Node, ValidatorNode
import pac2.pipe_template.validators.deepnest


# collect validations
validate_nodes = list(
    ProcessNode.iter_nodes_from_submodules(pac2.validators.deepnest)
)  # val node 1 - validation actions
print(validate_nodes)

# collect instances
strings = ["hello", "world", "hella", "hello"]
instance_nodes = [Node(s) for s in strings]
print(instance_nodes)

# node = DataNode(strings)  # todo good sample for adapter pattern

val_node = ValidatorNode(
    input_nodes=instance_nodes, validation_node=validate_nodes[0]
)  # val node 2 - validation hookup
val_node.eval()

print(val_node)
print(val_node.results)
print(val_node.linked_nodes[0].linked_nodes)
