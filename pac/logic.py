# session
#  collect_node
#    instance_wrap A
#      instance A
#    instance_wrap B
#      instance B
#  validator_node
#    get session, get plugins with instances(aka children)
#    run an action on each instance, result SUCCESS or FAIL (or WARNING/ custom)
import logging
# action can be attached and run on every node (right click in UI)
# repair/fix can use these actions
# validate node is an action, get the instance wrapper children and validate them

# create collect n validation plugins
# add fix action

# register UI
# register maya
# register collector
# register validator

# test this with the RPM pipeline
# import bpy


# ypu  cant run a node, you can run an action on a node
# nodes contain data and connections, and connect to action_nodes and instances
# action nodes can be run
# instances contain data like meshes, strings, ...

from typing import List, Type
from enum import Enum


def color_text(text, state):
    # color the text output
    if state == NodeState.SUCCEED:
        text = f'\033[32m{text}\033[0m'
    elif state == NodeState.FAIL:
        text = f'\033[31m{text}\033[0m'
    return text


# inspiration https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-map-state.html
# success could be 0, everything else is a failure/warning ...
class NodeState(Enum):
    INIT = "initialized"  # not run
    SUCCEED = "succeed"  # run and success, match AWS
    FAIL = "exception"  # run and exception, match AWS
    RUNNING = "running"  # run and running / in progress
    # PAUSED = "paused"
    # STOPPED = "stopped"
    # SKIPPED = "skipped"
    # DISABLED = "disabled"
    # PASS
    # WAIT
    # CHOICE


# class AdapterBrain(object):
#     def __init__(self):


class Adapter:
    # when we run on another node, sometimes we expect input of a certain type.
    # this is the adapter class, which can convert the input to the expected type
    # if there is a registered adapter

    type_input = None
    type_output = None

    def logic(self, data):
        """the logic that adapts the data to another type, override this"""
        raise NotImplementedError()

    def run(self, data):
        return self.logic(data)

    # input: instance(wrapper?)
    # output: int


class Node:
    def __init__(self, parent=None, name=None):
        # self.action_class = None
        self.actions = []

        # when you run a node, it runs all child nodes.
        # collectors create new DataNodes and make them children
        # validators run, with DataNodes as input
        #     results saved
        # actions run on ...

        # self.result = None  # run result # TODO ensure this can be identified as not run yet? combine w state?
        # self.results = []

        self.parent = parent  # node that created this node
        self.children = []  # nodes created by this node
        self.connections = []  # related nodes
        # TODO instead of storing result in 1 node, and then querying this node from the other node for the result.
        #  we can store the result in the link/connection between nodes

        self._state = NodeState.INIT
        self.continue_on_fail = True
        # self.name = name

    @property
    def state(self):
        # a session fails if any nodes in it fail
        # a collector fails if it fails to collect, it doesn't care about it's children
        # a validator fails if any of the datanodes it runs on fails
        # an instance node fails if any validations on it fail
        return self._state
        #
        # if self.children:
        #     # if this node has children, it's a collector, validator, or session
        #     # we check the state of the children
        #     for child in self.children:
        #         if child.state == NodeState.FAIL:
        #             return NodeState.FAIL
        #     return NodeState.SUCCEED
        # else:
        #     # if this node has no children, it's an instance node
        #     # we check the state of the instance node
        #     return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def session(self):
        """get the session this node belongs to (the top node)"""
        if self.parent:
            return self.parent.session
        else:
            return self

    def _run(self, *args, **kwargs):
        """inbetween function to handle state"""
        return self.logic()

    def logic(self):
        """inherit and overwrite this"""
        raise NotImplementedError

    def run(self, *args, **kwargs):
        # if we run the session, it runs all registered nodes under it.
        # e.g. collector first, then validate on the collected data
        # to ensure you first run collector and then validator, register in order.
        logging.info(f'running {self.__class__.__name__}')

        result = None
        try:
            self._state = NodeState.RUNNING
            result = self._run(*args, **kwargs)
            self._state = NodeState.SUCCEED
        except Exception as e:
            self._state = NodeState.FAIL
            logging.error(e)
            if not self.continue_on_fail:
                raise e

        # self.results.append(self.state)
        # self.result = result
        #
        # return result

    def pp_tree(self, depth=0):
        """
        Session ==>> initialized
          CollectHelloWorld ==>> succeed
            InstanceWrapper (Hello World)==>> initialized
          CollectHelloWorldList ==>> succeed
            InstanceWrapper (Hello)==>> initialized
            InstanceWrapper (World)==>> initialized
          ValidateHelloWorld ==>> failed
        """
        state = self._state

        state = color_text(state=state, text=state)

        txt = '  ' * depth + self.__class__.__name__ + '==>> ' + str(state) + '\n'
        for child in self.children:
            try:
                txt += child.pp_tree(depth=depth + 1).replace('==>>', f'({child.data})==>>')
            except AttributeError:
                txt += child.pp_tree(depth=depth + 1)
        if depth == 0:
            print(txt)
        return txt

    def print_result(self):
        txt = ""
        txt += f'{self}: {self.state}\n'
        for child in self.children:
            txt += child.print_result()


    def __repr__(self):
        return f'{self.__class__.__name__}'


class Action(Node):
    pass


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
            logging.error(e)
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


class Validator(Node):
    """
    a node that validates all collected instance nodes

    to implement, override self.logic(data)
    """
    required_type = None
    continue_on_fail = False

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.results = []  # store run stuff in here
        # self.required_type = None  # type of instance to validate

    @property
    def state(self):
        # a validator fails if any of the datanodes it runs on fails
        # or if the validator itself fails
        # TODO
        ...

        # if self.children:
        #     # if this node has children, it's a collector, validator, or session
        #     # we check the state of the children
        #     for child in self.children:
        #         if child.state == NodeState.FAIL:
        #             return NodeState.FAIL
        #     return NodeState.SUCCEED
        # else:
        #     # if this node has no children, it's an instance node
        #     # we check the state of the instance node
        #     return self._state



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

        # todo we alrdy save this in results.
        # why do we need connections too?
        self.connections.append(data_node)

        data_node.connections.append(self)
        try:
            state = NodeState.RUNNING
            result = self._validate_data_node(data_node=data_node)
            state = NodeState.SUCCEED
        except Exception as e:
            logging.error(e)
            state = NodeState.FAIL
            if not self.continue_on_fail:
                raise e

        self.results.append([data_node, state])

    # def run(self, *args, **kwargs):
    #     result = None
    #     try:
    #         self._state = NodeState.RUNNING
    #         result = self._run(*args, **kwargs)
    #         self._state = NodeState.SUCCEED
    #     except Exception as e:
    #         self._state = NodeState.FAIL
    #         logging.error(e)
    #         if not self.continue_on_fail:
    #             raise e

    def _run(self):  # create instances node(s)
        # 1. get the collectors from the session
        # 2. get the dataNodes from the collectors
        # 3. run validate on the mesh instances,
        # 4. create a backward link (to validate instance) in mesh instances
        self.results = []
        for data_node in self.iter_data_nodes():
            self.validate_data_node(data_node)

    def iter_data_nodes(self):
        """find matching data nodes of supported type"""
        for collector in self.session.iter_collectors(required_type=self.required_type):
            for data_node in collector.data_nodes:
                # this will get all data nodes
                # and assumes only collectors have children
                # todo refactor this.
                # atm all Node can have children but only session and collector use it.
                # validator would break if others also use it
                yield data_node

    def print_result(self):
        """
        ValidateIsTwo: NodeState.SUCCEED
          DataNode(1): fail
          DataNode(2): succeed
        """
        state = color_text(state=self.state, text=self.state)

        txt = f'{self.__class__.__name__}: {state}\n'
        for data_node, state in self.results:
            state = color_text(state=state, text=state)
            txt += f'  {data_node}: {state}\n'

        print(txt)
        return txt


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

                if required_type:
                    # if a type is required, only return collectors of matching type
                    if issubclass(collector.data_type, required_type):
                        yield collector
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


class DataNode(Node):
    """
    a DataNode can only contain 1 data-instance. (an instance can be a list)
    """
    def __init__(self, data, parent):
        # self.actions = []
        self.data = data  # custom data saved in the node
        super().__init__(parent=parent)

    @property
    def state(self):

        # other nodes, e.g. a validator, ran on a DataNode.
        # we collect the results of the nodes and return fail if any of them failed

        # TODO make this a dict
        # a connections is a node connected to 2 nodes
        # a connection can contain data.

        for node in self.connections:
            for result_node, result_state in node.results:
                if result_node != self:
                    continue
                if result_state == NodeState.FAIL:
                    state = NodeState.FAIL
                    return state
            # if node == self:
            #     return state

        state = NodeState.SUCCEED
        return state

    @state.setter
    def state(self, state):
        pass

    def __str__(self):
        return f'DataNode({self.data})'

    def __repr__(self):
        return f'DataNode({self.data})'
