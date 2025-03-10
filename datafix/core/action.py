from datafix.core.node import Node, node_state_setter


class Action(Node):
    def run(self):
        with node_state_setter(self):
            self.action()

    def action(self):
        """a action runs on a node"""
        raise NotImplementedError

    # actions usually run on collector nodes, or instances, or result nodes.

    # run on validator. e.g. select all wrong instances (material, mesh, ...)
    # run on result node from validator. select all wrong faces., select instance (mesh)
    # validator can assign actions to result nodes.
    # result nodes can auto inherit actions from their instance/data-node. wouldnt work for face ids though

    # makes more sense for validator to assign action to result node.
