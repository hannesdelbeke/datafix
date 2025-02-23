from datafix.node import Node


class ResultNode(Node):
    """store the outcome of a validation"""

    # there is overlap between a resultnode, and a outcome saved in the state. SUCCESS / FAIL / WARNING
    # POLISH: maybe combine in future?

    def __init__(self, data_node, parent):
        self.data_node: "datafix.datanode.DataNode" = data_node
        super().__init__(parent=parent)

    def __str__(self):
        return f'ResultNode({self.data_node.data})'

    @property
    def data(self):
        return self.data_node.data
