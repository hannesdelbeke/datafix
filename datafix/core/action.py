from datafix.core.node import Node, node_state_setter


class Action(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # hack remove from parent children.
        if self.parent:
            self.parent.children.remove(self)


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


class Run(Action):
    """ Action to re-run a Node, e.g. re-validate a validator."""
    def run(self):
        self.parent.run()