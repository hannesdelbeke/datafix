import typing
import copy
import logging
import pkgutil
import importlib
import importlib.util
import inspect
from enum import Enum
import traceback


# inspiration https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-map-state.html
# only process nodes can have these states: running, succeed, fail
# todo return code: success could be 0, everything else is a failure/warning ...
class NodeState(Enum):
    # pre run states
    INIT = "initialized"  # not run
    DISABLED = "disabled"
    # PASS # passes its input to its output, without performing work, mainly debugging

    # run states
    RUNNING = "running"  # run and running / in progress
    # PAUSED = "paused"

    # post run states
    SUCCEED = "succeed"  # run and success, match AWS
    FAIL = "exception"  # run and exception, match AWS
    # PASSED = "passed"


PRE_RUN_STATES = (NodeState.INIT, NodeState.DISABLED)
RUN_STATES = (NodeState.RUNNING,)
POST_RUN_STATES = (NodeState.SUCCEED, NodeState.FAIL)


connections = {}
# {
#     node_in: {attr_in_1: (node_out, attr_out, )), ...
# }

# __call__ is both IN and OUT
# { (all attrs from MODEL only, not NODE
#     node_in: {"__call__": (node_out, "__call__", )), ...  <--- trigger, after __call__out finished, start __call__in
#     node_in: {"mesh_name": (node_out, "__call__", )), ...  <--- get mesh name from a node __call__
#  XX don't do this --- node_in: {"__call__": (node_out, "test", )), ...  <--- trigger maybe? ignore for now
# }

# def add_connection(node_in, attr_in, node_out, attr_out="__call__"):
#     """add a connection between 2 nodes"""
#     data = connections.setdefault(node_in, {})
#     data[attr_in] = (node_out, attr_out)
#
# def remove_connection(node_in, attr_in):
#     """remove a connection between 2 nodes"""
#     data = connections.get(node_in, {})
#     data.pop(attr_in)
#
# def get_connections(node_in, attr_in):
#     """get all connections for a node attribute"""
#     data = connections.get(node_in, {})
#     return data.get(attr_in)
#
# def get_input_connections(node_in):
#     """get all input connections for a node"""
#     return connections.get(node_in, {})
#
# def iter_output_connections(node_out):
#     for node_in, data in connections.items():
#         for attr_in, value in data.items():
#             if value[0] == node_out:
#                 yield node_in, attr_in

# TODO convert to connections dict compatible w UI
# [ {
#       "out":[
#         "0x23d30810eb0",
#         "out"
#       ],
#       "in":[
#         "0x23d30813c70",
#         "in"
#       ]
#     }, ... ]


class NodeModel:
    """
    A (callable) data container that's stored in a Node, to avoid name clashes with Node attributes.
    The NodeModel lets you use any attribute name, except for '_node_meta_'
    self._node_meta_ is a reference to the Node that contains this NodeModel
    inherit and override __init__ to add attributes (use super!)
    override __call__ with the main callable
    """

    def __init__(self):
        self._node_meta_ = None

    def __getattribute__(self, item):
        value = super().__getattribute__(item)
        if item == "_node_meta_":
            return value
        if isinstance(value, Node):
            return value()
        return value

    def __setattr__(self, key, value):
        # e.g. key=="mesh" and value==Node
        if key != "_node_meta_" and isinstance(value, Node):
            self.connect(key, value, "__call__")
        super().__setattr__(key, value)

    # def connect(self, attr_in, node_out, attr_out):
    #     self._node_meta_.connect(node_out=node_out, attr_in=attr_in, attr_out=attr_out)


# if a node is callable, the class is callable?
# a pipeline is just hooking up methods with some config input.

# # todo do we need a wrapper for this. just data
# class NodeString(NodeModel):
#     def __init__(self, node):
#         super().__init__()
#         self.string = ""
#
#     def __call__(self, *args, **kwargs):
#         return self.string

# convert a class into a node
class NodeModelSample(NodeModel):
    # complete independent class, no overlap.
    # all methods are actions
    # all attributes are input/output controlled with GET SET
    # use _ for private/hidden attributes / properties

    def __init__(self, node):
        # super().__init__()
        self.mesh = None
        self.mesh_name: str = "cube"
        self.prefix: str = "p_"
        self.dupe_action = self.action_1  # could also insert callable node here.

    def action_1(self):
        print(self.mesh_name)

    def action_2(self):
        print("hello_world", self.prefix)
        # todo get node connections?

        # todo we want to know if the node failed or succeeded. access the node meta data _node_meta_
        # e.g. set material from failed meshes on a validation node. (can be done with self.failed_meshes)
        # todo store connection outside e.g. a global var

    def __call__(self, *args, **kwargs):
        # e.g. validate mesh
        assert self.mesh.name == self.mesh_name

    # TODO get set attr can be changed when we wrap in nodemeta


# default nodes are data nodes, which contain data
class Node:
    """
    a Node contains data or callable
    a Node (output) can be connected to other Node attributes (input)
    """

    _nodes = {}

    def __init__(self, data=None, name=None, state=None):
        """

        self.data contains pure data. if process node, it contains cached result?
        """

        #  --- CONNECTIONS ---
        # if we add a new node type attribute, add it to __getattribute__
        # self is node_IN
        self._output_links = {}  # {attr name_out: [(node_in, attr_name_IN), ...], ...}
        self._input_links = {}  # {attr name_in: (node_out, attr_name_OUT), ...}

        # id module + name
        self.name = name or self.__class__.__name__
        self.data = data  # data (like int, str, array,...) or settings for a processNode, class data vs instance data

        # actions need a name, and a callable. not just a method.
        # actions are optional.
        # actions are nodes that run on another node
        # self.actions = []  # callables or other nodes, actions to run on this node, same as callable attributes? call/run is an action too

        Node._nodes[id(self)] = self  # store all nodes, to check for unique id
        # self.runtime_connections = set()  # nodes used by this node during runtime, indirectly in callables

        # set init state at the end, so we can query if the init has finished.
        self._state = state or NodeState.INIT  # todo convert str to enum / property
        self.callbacks_state_changed = []

    def __call__(self) -> "typing.Any":  # run py code
        """returns the stored data, or the callable output if it's a CallableNodeBase"""
        return self.data

    def break_out_connection(self, attr_out, node_in, attr_in):
        """
        attr_out, the output attribute name
        node_in, the node that's connected to the output
        attr_in, the input attribute name from node_in, connected to attr_out
        """
        # remove in connection on node_in
        node_in._input_links.pop(attr_in)

        # remove out connection on self
        out_list = self._output_links.setdefault(attr_out, [])
        for node, attr in out_list:
            if node == node_in and attr == attr_in:
                out_list.remove((node, attr))
                break

        # don't track attr_out if connection list is empty
        if not out_list:
            self._output_links.pop(attr_out)

    def connect(self, node_in, attr_out=None, attr_in=None):
        """
        node_in is the node with the IN port
        (self) node_out is the node with the OUT port
        A -> B: node A is the out node since its output is connected to node B input
        """
        node_out = self
        # method chat gpt, based on connect_in, but reversed
        # todo double check logic

        if not attr_out:
            attr_out = "__call__"
        if not attr_in:
            attr_in = "__call__"

        # todo check if attr exists

        # cleanup old out connection, on the old node_out
        # from node in, get the old out node, and the old out attr
        data = node_in._input_links.get(attr_in)  # get (B, __call__) from C
        if data:
            old_out_node, old_out_attr = data
            old_out_node.break_out_connection(old_out_attr, node_in, attr_in)

        # Override old out connection
        # todo check not already connected
        node_out._output_links.setdefault(attr_out, []).append((node_in, attr_in))

        # Set new in connection
        node_in._input_links[attr_in] = (node_out, attr_out)

    # def connect(self, node_out, attr_in: str, attr_out: str):
    #     """
    #     connect 2 nodes, assuming self is the input node
    #     """
    #     node_in = self
    #
    #     # todo check if attr-in is an input, and attr_out is an output
    #     # defaults to input, if not specified
    #     # GET means output, SET means input
    #     # GET SET means both
    #     # we assume user didn't make a mistake, else Python will raise error for us.
    #     # attr_in_value = getattr(node_in, attr_in)
    #     # attr_out_value = getattr(node_out, attr_out)
    #
    #     # check if node is already connected
    #
    #     pass

    # def __getattribute__(self, item) -> "typing.Any":
    #
    #     # todo this only triggers for attributes, not for indirect attributes like self.data.attr_name
    #     #  also not handling iterables yet, and deep level iters.
    #     #  also how to avoid triggering a generator, when you check the value is a node
    #
    #     value = super().__getattribute__(item)
    #
    #     # state should never contain a node, return to prevent a getattribute loop
    #     if item in ("_state"):
    #         return value
    #     # # track runtime connections between Nodes
    #     # finished_init = hasattr(self, "_state")
    #     # if callable(value) and item != "__class__" and finished_init:
    #     #     frames = inspect.stack()
    #     #     # search the callstack for the first Node
    #     #     for f in frames:
    #     #         caller_frame = f.frame.f_back
    #     #         if not caller_frame:
    #     #             continue
    #     #         caller_object = caller_frame.f_locals.get("self")
    #     #         if isinstance(caller_object, Node) and caller_object != self:
    #     #             # todo also save method name / attr where the node is used
    #     #             self.runtime_connections.add(caller_object)
    #     #             caller_object.runtime_connections.add(self)
    #     #             break
    #
    #     # TODO only IN trigger, and OUT trigger should contain nodes
    #
    #     # if value is a Node, run it and return the result
    #     # exception for __class__ attr which always is of type Node
    #     if isinstance(value, Node) and item not in (
    #         "__class__",
    #         "_Node__output_links",
    #         "output_links",
    #         "__call__",
    #         "callable",
    #     ):
    #         value = value.__call__()
    #
    #     return value

    # def __setattr__(self, key, value) -> None:
    #
    #     # todo this only triggers for attributes, not for indirect attributes like self.data.attr_name
    #     #  also not handling iterables yet, and deep level iters.
    #     #  also how to avoid triggering a generator, when you check the value is a node
    #
    #     super().__setattr__(key, value)
    #
    #     # don't track Node if it's a property, else attributes are duplicated in self._output_links
    #     # e.g. {'_Node__parent': Node(b), 'parent': Node(b)}
    #     if key not in self.__dict__:
    #         return
    #
    #     if isinstance(value, Node):
    #         value._output_links[key] = self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"  # e.g. Node(hello)

    # def iter_input_nodes(self) -> "typing.Generator[Node]":
    #     """iterate over all input nodes"""
    #     for attr_name, value in self.__dict__.items():
    #         if callable(value) and not isinstance(value, Node):
    #             continue
    #         if attr_name in ("input_nodes", "connected_nodes", "OUT"):  # skip methods that call this method
    #             continue
    #         if isinstance(value, Node):
    #             yield value

    # # todo avoid triggering a generator, when you check the value is a node
    # #  might be unwanted
    # # check list, set, dict, ...
    # try:
    #     for item in value:
    #         if isinstance(item, Node):
    #             yield item
    # except TypeError:
    #     pass

    @property
    def state(self) -> "NodeState":
        return self._state

    @state.setter
    def state(self, state: "NodeState") -> None:
        """set the node state and run callbacks"""
        self._state = state
        for callback in self.callbacks_state_changed:
            callback(state)

    @property
    def input_nodes(self) -> "typing.List[Node]":
        """nodes connected to attributes of this node"""
        # return list(self.iter_input_nodes())
        # print("self._input_links", self._input_links)
        return [node for node, attr_name in self._input_links.values()]

    @property
    def output_nodes(self) -> "typing.List[Node]":
        """nodes connected to this node output"""
        # _output_links is a dict with attr_name: [(node, attr_name), ...]
        # convert to list of nodes
        nodes = []
        for tuple_list in self._output_links.values():
            for node, attr_name in tuple_list:
                nodes.append(node)
        return nodes

    @property
    def output_links(self) -> "typing.Dict[str, Node]":
        """return dict of output links, where key is the attribute name, and value is the node"""
        return self._output_links

    @property
    def connected_nodes(self) -> "typing.Set[Node]":
        """return all connected nodes"""
        return set(self.input_nodes) | set(self.output_nodes)

    # def graph(self):
    # get all connected nodes

    # def deserialize(self, data):  # todo
    #     """load data from dict"""
    #     for attr, value in data.items():
    #         if isinstance(value, dict):
    #             node = Node()
    #             node.deserialize(value)
    #             setattr(self, attr, node)
    #         else:
    #             setattr(self, attr, value)
    #     pass

    def serialize(self, bake_data=False):
        """convert to dict"""  # todo save data to json / needs lots of work cleanup
        node_config = copy.deepcopy(self.__dict__)  # prevent mutating self.__dict__
        # # edges = [] # todo support edge attrs
        # for attr_name, value in dct.items():
        #     if isinstance(value, Node):
        #         if bake_data:
        #             dct[attr_name] = value.__call__()
        #         # else:
        #         #     dct[attr_name] = None
        #         # edges.append((id(self), attr_name, value.id))
        #
        #     # todo recursive serialise. when we dont have a node.
        #     #  e.g. support nodes in arrays in attributes

        node_config["_state"] = (
            node_config["_state"].name if isinstance(node_config["_state"], Enum) else node_config["_state"]
        )  # todo cleanup

        return node_config

    def config(self):
        """convert to config dict"""
        config = self._raw_config()

        config["root"] = id(self)

        # cleanup config
        for node_config in config["nodes"]:
            for attr_name in ("_Node__children", "_Node__output_links", "_Node__parent"):
                del node_config[attr_name]

        return config

    def _raw_config(self, _collected_nodes=None, _config=None):
        """helper func to convert to config dict, without cleanup"""
        config = _config or {}
        config["nodes"] = node_configs = config.get("nodes", [])
        config["edges"] = edges = config.get("edges", [])  # todo support edge attrs

        collected_nodes = _collected_nodes or set()

        # export node, and all connected nodes.
        for node in self.connected_nodes:

            # recursive
            if node in collected_nodes:
                continue
            collected_nodes.add(node)
            node._raw_config(collected_nodes, config)

            # collect nodes
            node_config = node.serialize()
            node_configs.append(node_config)

            # edges  # todo avoid collecting the same edge in 2 directions
            for attr_name, value in node_config.items():
                if isinstance(value, Node):
                    edges.append((id(node), attr_name, id(value)))

        return config

    @classmethod
    def graph_from_config(cls, config, new_if_exists=False):
        """
        create a graph from a config dict
        you can also load multiple partial configs
        """
        node_configs = config["nodes"]
        edge_configs = config["edges"]
        root_id = config["root"]
        root_node = None

        # create or reuse existing nodes & set attributes
        for node_config in node_configs:
            if new_if_exists:
                node = cls(**node_config)
            else:
                # todo not just check id, maybe match by name
                node = cls._nodes.get(node_config["id"])

            if id(node) == root_id:
                root_node = node

        # connect existing nodes
        for edge_config in edge_configs:
            node_id, attr_name, target_id = edge_config
            node = cls._nodes[node_id]
            target_node = cls._nodes[target_id]
            setattr(node, attr_name, target_node)

        return root_node

    # def _replace_node(self, value):
    #
    #     # also handle lists and dicts with nodes
    #     if isinstance(value, list):
    #         for i, item in enumerate(value):
    #             if isinstance(item, Node):
    #                 dct[attr_name][i] = item.id
    #     if isinstance(value, dict):
    #         for k, v in value.items():
    #             if isinstance(v, Node):
    #                 dct[attr_name][k] = v.id
    #     if isinstance(value, set):
    #         for i, item in enumerate(value):
    #             if isinstance(item, Node):
    #                 dct[attr_name][i] = item.id  # todo can you set set by index?

    @classmethod
    def collect_node_classes_from_module(cls, module, recursive=True) -> "typing.Generator[CallableNodeBase]":
        """find all Node classes in a module & its submodules"""

        for attr_name in dir(module):
            if attr_name.startswith('_'):  # skip private classes
                continue
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, Node):
                yield attr

        if recursive and hasattr(module, '__path__'):
            for loader, submodule_name, is_pkg in pkgutil.walk_packages(module.__path__, module.__name__ + '.'):
                spec = importlib.util.find_spec(submodule_name)
                if spec is None:
                    continue
                submodule = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(submodule)
                # recursive=False because walk_packages is already recursive
                for _cls in cls.collect_node_classes_from_module(submodule, recursive=False):
                    # check node is not just imported in the module, but actually defined in the module
                    if "pac2.node" in _cls.__module__:
                        continue
                    yield _cls

    @classmethod
    def nodes_from_module(cls, module, recursive=True) -> "typing.Generator[Node]":
        """create nodes from all Node classes in a module"""
        for node_class in cls.collect_node_classes_from_module(module, recursive=recursive):
            node = node_class()
            yield node


class ProcessNode(Node):  # todo rename CallNode
    def __init__(self, callable=None, raise_exception=False, name=None, *args, **kwargs):
        """
        raise_exception: if True, raise exception when callable fails, else node saves exception in self.state. used for debugging
        """
        super().__init__(*args, **kwargs)
        # self.IN = None  # input trigger, nodes (callables) to run this node

        # todo can OUT be same as data?
        # self.OUT = None  # output trigger to run the next node, requires IN nodes to SUCCEED

        self.callable = callable  # could be a callable, or a NodeModel. result cached in self.data
        self.name = name or callable.__name__ if callable else self.__class__.__name__
        self.continue_on_error = False  # warning or error. stop or continue the node flow on exception
        self.raise_exception = raise_exception  # debugging

    def start(self, *args, **kwargs):
        """
        starts the pipeline. call this node, then start the next node, until finished or exception
        passes args and kwargs to all callables/nodes
        """
        print("START", self, args, kwargs)
        self(*args, **kwargs)
        if self.OUT:
            self.OUT.start(*args, **kwargs)

    # def __setattr__(self, key, value):
    #     super().__setattr__(key, value)
    #     if key == "OUT":
    #         # if provided None with a node stored, reset it, and reset the connection on the node
    #         if value is None and self.OUT:
    #             self.OUT.IN = None
    #             self.OUT = None
    #             return
    #
    #         # assume it's a node and create a bidirectional link
    #         if value and value.IN != self:
    #             print("seeting out", value, self, "current out", value.OUT)
    #             value.IN = self

    # if key == "IN":
    #     # if provided None with a node stored, reset it, and reset the connection on the node
    #     if value is None and self.IN:
    #         self.IN.OUT = None
    #         self.IN = None
    #         return
    #
    #     # assume it's a node and create a bidirectional link
    #     if value and value.OUT != self:
    #         print("seeting out", value, self, "current out", value.OUT)
    #         value.OUT = self

    # def __gt__(self, other):
    #     # link nodes
    #     print("linking", self, other)
    #     self.OUT = other
    #     return other

    def __call__(self, *args, **kwargs) -> "typing.Any":  # protected method
        # check if all input nodes have run
        if self.state == NodeState.SUCCEED:
            return self.data

        for node in self.input_nodes:
            # check if type is process node
            if isinstance(node, ProcessNode):
                if node.state == NodeState.INIT:  # if DISABLED or already run, don't run
                    node()
                    if node.state != NodeState.SUCCEED:
                        self.state = NodeState.FAIL
                        if not self.continue_on_error:
                            return

        if self.state == NodeState.DISABLED:
            return
        try:
            self.state = NodeState.RUNNING
            result = self.callable(*args, **kwargs)  # todo does this pass self?
            self.state = NodeState.SUCCEED
            # todo no need to cache result, instead create a new datanode with the result
            # for a validation, result would be true or false, with failed instances.
            self.data = result  # todo choose if we use data to cache result, or if we use it for settings. e.g. which tri-count to validate against
            return result
        except Exception as e:
            self.state = NodeState.FAIL
            if self.raise_exception:
                raise e
            else:
                logging.error(f"Failed to run {self.name}: {e}")
                traceback.print_exc()
            return

    # @classmethod
    # def from_module(cls, module: "str|types.ModuleType", method_name=None) -> "CallableNodeBase":
    #     """
    #     create a CallableNodeBase from a module with method'
    #
    #     Args:
    #         module: module name or module object
    #         method_name: method name to run, default is 'main'
    #     """
    #     if isinstance(module, str):
    #         module_name = module
    #         method_name = method_name or 'main'
    #         module = importlib.import_module(module_name)
    #
    #     callable = getattr(module, method_name)
    #     n = cls(callable)
    #     n.name = f"{module_name}.{method_name}"

    @classmethod  # todo comment out because swap to callable
    def node_from_module_method(
        cls, module, method_name=None
    ) -> "CallableNodeBase":  # todo can we combine module & method_name kwarg
        """create a CallableNodeBase from a module with method 'main'"""
        method_name = method_name or 'main'
        callable = getattr(module, method_name)
        n = cls(callable)
        n.name = f"{module.__name__}.{method_name}"  # module + method name
        return n

    @classmethod
    def iter_nodes_from_submodules(cls, parent_module) -> "typing.Generator[CallableNodeBase]":
        """create ProcessNodes generator from all submodules in a module"""

        for module_info, name, is_pkg in list(pkgutil.iter_modules(parent_module.__path__)):
            spec = module_info.find_spec(name)
            module = importlib.util.module_from_spec(spec)
            module = importlib.import_module(f'{parent_module.__name__}.{module.__name__}')

            node = cls.node_from_module(module)
            yield node


def import_module_from_path(module_path) -> "types.ModuleType|None":

    try:
        spec = importlib.util.spec_from_file_location("custom_module", str(module_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logging.error(f"Failed to import module from path: {module_path}")
        logging.error(f"Error: {e}")
        return None


# todo validate different nodes, compared to each other
# todo validate different nodes, each one individually
class ValidatorNode(ProcessNode):
    """check that all input nodes pass the validation"""

    def __init__(self, continue_on_fail=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.continue_on_fail = continue_on_fail

        # self.add_input_nodes(input_nodes or [])  # todod option to link input node to any attribute of this node

    def __call__(self):  # todo
        if self.validation_node.state == NodeState.DISABLED:
            return

        for node in self.iter_input_nodes():
            if self.validation_node.state == NodeState.FAIL:
                self.state = NodeState.FAIL
                return  # todo stop or continue on fail

            self.validation_node.__call__(node)
            if node.state != NodeState.SUCCEED:
                self.state = NodeState.FAIL
                return

    # def add_input_nodes(self, nodes):  # todo link slotname node
    #     self.input_nodes.extend(nodes)
    #     for node in nodes:
    #         node.linked_nodes.append(self)

    @property
    def results(self):
        return [node.state for node in self.input_nodes]


# todo test cache output
# run a process node, save  result in a data node
# serialise it, deserialise it :)
# now we can restart our workflow from a saved state


class MeshVal(ProcessNode):
    class SlotsIn:
        actions = []
        mesh_name_prefix = ""

    class SlotsOut:
        output = None
