from datafix.node import Node, NodeState
from datafix.datanode import DataNode


class Collector(Node):  # session plugin (context), session is a node
    """
    a collector finds & stores data node, & saves them in self.children

    e.g. a mesh collector finds all meshes in the Blender scene
    and creates a DataNode for each mesh, storing the mesh data in the DataNode

    override logic() to implement your collector
    """
    # def __init__(self, parent):
    #     super().__init__(parent=parent)
    #     self.continue_on_fail = False

    @property
    def data_nodes(self):
        # convenience method to get all instance nodes, children is too abstract
        return self.children

    def run(self, *args, **kwargs):
        # if we run the session, it runs all registered nodes under it.
        # e.g. collector first, then validate on the collected data
        # to ensure you first run collector and then validator, register in order.

        result = None
        try:
            self.state = NodeState.RUNNING
            result = self.logic(*args, **kwargs)

            # ------------------------
            for instance in result:
                node = DataNode(instance, parent=self)
                self.data_nodes.append(node)
            # ------------------------

            self.state = NodeState.SUCCEED
        except Exception as e:
            self.state = NodeState.FAIL
            self.log_error(f"'{self.__class__.__name__}' failed running:'{e}'" )
            if not self.continue_on_fail:
                raise e

    @property
    def data_type(self):
        """return the type of data this collector collects"""
        if self.data_nodes:
            return type(self.data_nodes[0].data)
        return None

    def logic(self):  # create instances node(s)
        """override this with your implementation, returning a list of data"""
        raise NotImplementedError
