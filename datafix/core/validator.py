from datafix.core.resultnode import ResultNode
from datafix.core.node import Node, NodeState
import datafix.core.utils


class Validator(Node):
    """
    a node that validates all collected instance nodes

    to implement, override self.logic(data)

    # results are saved in self.children
    """
    required_type = None

    def _validate_data(self, data):
        """validate the data in the DataNode"""
        adapted_data = self.session.adapt(data, self.required_type)
        # todo validator shouldn't care about adapter, node or session mngr should handle this
        return self.logic(adapted_data)

    def logic(self, data):
        """the logic to validate the data, override this"""
        raise NotImplementedError()

    def validate_data_node(self, data_node):
        # public method, don't override this
        # atm not used by anything else but will be used by UI to right click revalidate
        """run the validation logic on a DataNode, and save the result in a ResultNode"""
        try:
            result = self._validate_data(data=data_node.data)
            # # todo how to support return value and fail/raise error at same time
            state = NodeState.SUCCEED
        except Exception as e:
            self.log_error(f"'{data_node}' failed validation `{self.__class__.__name__}`:'{e}'" )
            state = NodeState.FAIL
            if not self.continue_on_fail:
                raise e

        return ResultNode(data_node, parent=self, state=state, warning=self.warning)

    def _run(self):  # create instances node(s)
        # 1. get the collectors from the session
        # 2. get the DataNodes from the collectors
        # 3. run validate on the mesh instances,
        # 4. create a backward link (to validate instance) in mesh instances
        for _ in self._iter_validate_data_nodes():
            ...
        datafix.core.utils.set_state_from_children(self)

    def _iter_validate_data_nodes(self):
        for data_node in self._iter_data_nodes():
            result_node = self.validate_data_node(data_node)
            yield result_node

    def _iter_data_nodes(self):
        """find matching data nodes of supported type"""
        # default behaviour is to implicitly find any data node of required type
        # override this method if you explicitly want to control collector input.
        for collector in self.session.iter_collectors(required_type=self.required_type):
            print(collector)
            for data_node in collector.data_nodes:
                yield data_node
