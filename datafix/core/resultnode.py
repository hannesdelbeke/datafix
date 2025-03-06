from datafix.core.node import Node
from datafix.core.datanode import DataNode


class ResultNode(Node):
    """store the outcome of a validation"""

    # there is overlap between a resultnode, and a outcome saved in the state. SUCCESS / FAIL / WARNING
    # POLISH: maybe combine in future?

    def __init__(self, data_node, state, warning, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_node: DataNode = data_node
        data_node.result_nodes.append(self)  # creates bi-directional link
        self.state = state
        self.warning = warning

    def __str__(self):
        return f'ResultNode({self.data_node.data})'

    @property
    def data(self):
        return self.data_node.data
