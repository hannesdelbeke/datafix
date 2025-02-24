from datafix.resultnode import ResultNode
from datafix.node import Node, NodeState


class Validator(Node):
    """
    a node that validates all collected instance nodes

    to implement, override self.logic(data)

    # results are saved in self.children
    """
    required_type = None

    def __init__(self, parent):
        super().__init__(parent=parent)
        # self.required_type = None  # type of instance to validate

    @property
    def state(self):
        # a validator fails if any of the DataNodes it runs on fails
        # or if the validator itself fails
        if self._state != NodeState.SUCCEED:
            return self._state

        result_states = [node.state for node in self.children]
        if NodeState.FAIL in result_states:
            return NodeState.FAIL
        elif NodeState.WARNING in result_states:
            return NodeState.WARNING
        else:
            return NodeState.SUCCEED

    def _validate_data(self, data):
        """validate the data in the DataNode"""
        adapted_data = self.session.adapt(data, self.required_type)
        # todo validator shouldn't care about adapter, node or session mngr should handle this
        return self.logic(adapted_data)

    def logic(self, data):
        """the logic to validate the data, override this"""
        raise NotImplementedError()

    def _validate_data_node(self, data_node):
        # you can override this one, but you wont have an automated adapter though
        return self._validate_data(data=data_node.data)

    def validate_data_node(self, data_node):
        # public method, don't override this

        # todo we already save this in results.
        # why do we need connections too?
        self.connections.append(data_node)

        data_node.connections.append(self)
        try:
            self._validate_data_node(data_node=data_node)
            state = NodeState.SUCCEED
        except Exception as e:
            self.log_error(f"'{data_node}' failed validation `{self.__class__.__name__}`:'{e}'" )
            state = NodeState.FAIL
            if not self.continue_on_fail:
                raise e

        # check if we allow warnings
        if self.warning and state == NodeState.FAIL:
            state = NodeState.WARNING

        # save results_nodes in self.children
        result_node = ResultNode(data_node, parent=self)
        result_node.state = state
        data_node.connections.append(result_node)  # bi-directional link
        self.children.append(result_node)

    def _run(self):  # create instances node(s)
        # 1. get the collectors from the session
        # 2. get the dataNodes from the collectors
        # 3. run validate on the mesh instances,
        # 4. create a backward link (to validate instance) in mesh instances
        for data_node in self.iter_data_nodes():
            self.validate_data_node(data_node)

    def iter_data_nodes(self):
        """find matching data nodes of supported type"""
        for collector in self.session.iter_collectors(required_type=self.required_type):
            print(collector)
            for data_node in collector.data_nodes:
                # this will get all data nodes
                # and assumes only collectors have children
                # todo refactor this.
                # atm all Node can have children but only session and collector use it.
                # validator would break if others also use it
                yield data_node
