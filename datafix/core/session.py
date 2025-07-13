import logging
from typing import Type, List, TYPE_CHECKING, Optional, Generator
from datafix.core.collector import Collector
from datafix.core.node import Node, NodeState, node_state_setter


__active_session: "Optional[Session]" = None


class Session(Node):
    """some kind of canvas or context, that contains plugins etc"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global __active_session
        __active_session = self
        self.adapters = []

    def append(self, node: Type[Node]):
        # convenience method to add a node to the session, unsure if i ll keep it
        return node(parent=self)

    def iter_collectors(self, required_type=None) -> "Generator[Collector]":
        """return all collectors that collect the required type"""
        for node in self.children:
            if not isinstance(node, Collector):
                continue

            collector: Collector = node

            # todo support list of type x
            #  e.g. List[Type[Mesh]]

            if required_type:
                # if a type is required, only return collectors of matching type
                if collector.data_type and issubclass(collector.data_type, required_type):
                    yield collector
                else:
                    logging.info(f"collector '{collector}' does not match datatype '{required_type}'")
            else:
                # no required type, allow all collectors
                yield collector

    def run(self):
        self.state = NodeState.RUNNING
        for node in self.children:
            with node_state_setter(node):
                node.run()
        self.set_state_from_children()

    def adapt(self, instance, required_type: "type"):
        if not required_type:
            # there is no required type, so we collect all instances
            return instance

        if isinstance(instance, required_type):
            # there is a required type, so we only collect instances of this type
            return instance

        # for all other instances not of the matching type, we attempt to adapt to type
        # if possible we collect, if no adapter is found, we skip the instance
        # this should not fail, but skip! # todo
        for adapter in self.adapters:
            if adapter.type_output == required_type and type(instance) in adapter.input_types:
                return adapter.run(instance)
        return None

    def register_adapter(self, adapter):
        self.adapters.append(adapter)

    def __str__(self) -> str:
        return f"Session({self.name})"


def get_active_session():
    """
    use method to get active session instead of a global variable.
    Else sometimes other modules reference the old session
    """
    global __active_session

    return __active_session or Session(name="default session")
