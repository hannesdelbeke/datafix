import logging
from typing import List, Type
from datafix.core.collector import Collector
from datafix.core.node import Node, NodeState


class Session(Node):
    """some kind of canvas or context, that contains plugins etc"""
    def __init__(self):
        self.nodes: List[Type[Node]] = []
        self.adapters = []
        super().__init__()

    def add(self, node):
        self.nodes.append(node)

    def iter_collectors(self, required_type=None) -> Collector:
        for node in self.node_instances:
            if isinstance(node, Collector):
                collector = node

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

    @property
    def node_instances(self):
        """get all instanced nodes,
        since we register the classes, we can create instances"""
        return self.children

    # @property
    # def collected_instances(self):
    #     return self.children

    def run(self):
        self.state = NodeState.RUNNING
        for plugin_class in self.nodes:
            plugin_instance = plugin_class(parent=self)
            self.node_instances.append(plugin_instance)
            plugin_instance.run()
        # todo set success and fail on session

        # if none if the children failed, succeed
        if all([node._state == NodeState.SUCCEED for node in self.node_instances]):
            self.state = NodeState.SUCCEED
        else:
            self.state = NodeState.FAIL

        # create collector instance and track in session, create backward link in collect instance
        # collector.run(session)
        # store mesh instances in the collector instance, create backward link in mesh instances

        # create validator instance and track in session, create backward link in validator instance
        # validator.run(session)
        # get the collect instances from session, get the mesh instances from collect instances,
        # run validate on the mesh instances, create backward link (to validate inst) in mesh instances

        # create export instance and track in session, create backward link in export instance
        # export.run(session)
        # get the collect instances from session, get mesh inst from collect inst.
        # run export on the mesh instances, create backward link (to export inst) in mesh instances

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
