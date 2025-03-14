from datafix.core.node import Node, NodeState, node_state_setter
from datafix.core.datanode import DataNode
from datafix.core.action import Action, Run


class Collector(Node):  # session plugin (context), session is a node
    """
    a collector finds & stores data nodes, & saves them in self.children

    e.g. a mesh collector finds all meshes in the Blender scene
    and creates a DataNode for each mesh, storing the mesh data in the DataNode

    override self.collect() to implement your collector
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions = [Run(parent=self)]

    @property
    def data_nodes(self):
        # convenience method to get all instance nodes, children is too abstract
        return self.children

    def run(self, *args, **kwargs):
        # clear all children, except actions which are assigned on init
        children_to_delete = [child for child in self.children if not isinstance(child, Action)]
        for child in children_to_delete:
                child.delete()

        with node_state_setter(self):
            result = self.collect(*args, **kwargs)
            for data_item in result:
                DataNode(data=data_item, parent=self, name=data_item)

    @property
    def data_type(self):
        """
        returns the type of data this collector collects, inferred from collected data.
        override to make it explicit
        """
        if self.data_nodes:
            return type(self.data_nodes[0].data)
        return None

    def collect(self):  # create instances node(s)
        """returns a list of data, each list item is then automatically stored in a DataNode"""
        raise NotImplementedError  # override this with your implementation
