from datafix.core.node import Node, NodeState


class DataNode(Node):
    """
    a DataNode can only contain 1 data-instance. (an instance can be a list)
    """
    def __init__(self, data, *args, **kwargs):
        self.data = data  # custom data saved in the node
        self.result_nodes = []  # result nodes created by the validator(s) that ran on this node
        super().__init__(*args, **kwargs)

    @property
    def state(self):
        # validator(s) ran on this DataNode,
        # creating resultNode(s) with the validation result saved in the state
        # this node fails if any result nodes failed

        result_nodes = [node for node in self.result_nodes]
        result_nodes_states = [node.state for node in result_nodes]

        if NodeState.FAIL in result_nodes_states:
            return NodeState.FAIL
        elif NodeState.WARNING in result_nodes_states:
            return NodeState.WARNING
        else:
            return NodeState.SUCCEED

    @state.setter
    def state(self, state):
        pass

    def __str__(self):
        return f'DataNode({self.data})'
