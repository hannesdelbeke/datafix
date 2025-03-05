from datafix.core.node import Node, NodeState, node_state_setter
from datafix.core.datanode import DataNode


class Collector(Node):  # session plugin (context), session is a node
    """
    a collector finds & stores data node, & saves them in self.children

    e.g. a mesh collector finds all meshes in the Blender scene
    and creates a DataNode for each mesh, storing the mesh data in the DataNode

    override logic() to implement your collector
    """

    @property
    def data_nodes(self):
        # convenience method to get all instance nodes, children is too abstract
        return self.children

    def run(self, *args, **kwargs):
        # if we run the session, it runs all registered nodes under it.
        # e.g. collector first, then validate on the collected data
        # to ensure you first run collector and then validator, register in order.
        with node_state_setter(self):
            result = self.collect(*args, **kwargs)
            for instance in result:
                DataNode(instance, parent=self)

    @property
    def data_type(self):
        """
        returns the type of data this collector collects
        default it's the type of the first data node, so type is inferred from the data.
        feel free to override this to make it explicit
        """
        if self.data_nodes:
            return type(self.data_nodes[0].data)
        return None

    def collect(self):  # create instances node(s)
        """returns a list of data, each list item is then automatically stored in a DataNode"""
        raise NotImplementedError  # override this with your implementation
