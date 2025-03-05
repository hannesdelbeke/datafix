import logging
from typing import List, Type

from datafix.core.collector import Collector
from datafix.core.node import Node, NodeState
import datafix.core.utils


class Session(Node):
    """some kind of canvas or context, that contains plugins etc"""
    def __init__(self):
        super().__init__()
        global active_session
        active_session = self
        self.nodes: List[Type[Node]] = []  # registered nodes, usually classes but can be instances.
        self.adapters = []

    def iter_collectors(self, required_type=None) -> Collector:
        for node in self.children:
            if not isinstance(node, Collector):
                continue

            collector: Collector = node

            # todo support list of type x
            #  e.g. List[Type[Mesh]]

            if required_type:
                print(collector, collector.data_type, required_type)
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
            node.run()
        datafix.core.utils.state_from_children(self)

    def adapt(self, instance, required_type):
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
            if adapter.type_output == required_type and adapter.type_input == type(instance):
                return adapter.run(instance)
        return None

    def register_adapter(self, adapter):
        self.adapters.append(adapter)


active_session = Session()