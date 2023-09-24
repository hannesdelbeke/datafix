import typing
import copy
import logging
import pkgutil
import importlib
import importlib.util
import inspect
from enum import Enum

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
        self.__output_links = {}  # when node is an input node for another node, dict with {attr name: node, ...}

        # id module + name
        self.name = name or self.__class__.__name__
        self.data = data  # data (like int, str, array,...) or settings for a processNode, class data vs instance data

        # actions need a name, and a callable. not just a method.
        # actions are optional.
        # actions are nodes that run on another node
        # self.actions = []  # callables or other nodes, actions to run on this node, same as callable attributes? call/run is an action too

        Node._nodes[id(self)] = self  # store all nodes, to check for unique id
        self.runtime_connections = set()  # nodes used by this node during runtime, indirectly in callables

        # set init state at the end, so we can query if the init has finished.
        self.state = state or NodeState.INIT  # todo convert str to enum / property

    def __call__(self) -> "typing.Any":  # run py code
        """returns the stored data, or the callable output if it's a ProcessNode"""
        return self.data

    def __getattribute__(self, item) -> "typing.Any":

        # todo this only triggers for attributes, not for indirect attributes like self.data.attr_name
        #  also not handling iterables yet, and deep level iters.
        #  also how to avoid triggering a generator, when you check the value is a node

        value = super().__getattribute__(item)

        # state should never contain a node, return to prevent a getattribute loop
        if item in ("state"):
            return value

        finished_init = hasattr(self, "state")

        if callable(value) and item != "__class__" and finished_init:
            frames = inspect.stack()
            # search the callstack for the first Node
            for f in frames:
                caller_frame = f.frame.f_back
                if not caller_frame:
                    continue

                caller_object = caller_frame.f_locals.get("self")

                if isinstance(caller_object, Node) and caller_object != self:
                    # todo also save method name / attr where the node is used
                    self.runtime_connections.add(caller_object)
                    caller_object.runtime_connections.add(self)
                    break

        # if value is a Node, run it and return the result
        # exception for __class__ attr which always is of type Node
        if isinstance(value, Node) and item not in (
            "__class__",
            "_Node__output_links",
            "output_links",
            "__call__",
            "callable",
        ):
            value = value.__call__()

        return value

    def __setattr__(self, key, value) -> None:

        # todo this only triggers for attributes, not for indirect attributes like self.data.attr_name
        #  also not handling iterables yet, and deep level iters.
        #  also how to avoid triggering a generator, when you check the value is a node

        super().__setattr__(key, value)

        # don't track Node if it's a property, else attributes are duplicated in self.__output_links
        # e.g. {'_Node__parent': Node(b), 'parent': Node(b)}
        if key not in self.__dict__:
            return

        if isinstance(value, Node):
            value.__output_links[key] = self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"  # e.g. Node(hello)

    def iter_input_nodes(self) -> "typing.Generator[Node]":
        """iterate over all input nodes"""
        for attr_name, value in self.__dict__.items():
            if callable(value) and not isinstance(value, Node):
                continue
            if attr_name in ("input_nodes", "connected_nodes", "OUT"):  # skip methods that call this method
                continue
            if isinstance(value, Node):
                yield value

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
    def input_nodes(self) -> "typing.List[Node]":
        """nodes connected to attributes of this node"""
        return list(self.iter_input_nodes())

    @property
    def output_nodes(self) -> "typing.List[Node]":
        """nodes connected to this node output"""
        return list(self.__output_links.values())

    @property
    def output_links(self) -> "typing.Dict[str, Node]":
        """return dict of output links, where key is the attribute name, and value is the node"""
        return self.__output_links

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

        node_config["state"] = (
            node_config["state"].name if isinstance(node_config["state"], Enum) else node_config["state"]
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
    def collect_node_classes_from_module(cls, module, recursive=True) -> "typing.Generator[ProcessNode]":
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
        self.IN = None  # input trigger, nodes (callables) to run this node

        # todo can OUT be same as data?
        self.OUT = None  # output trigger to run the next node, requires IN nodes to SUCCEED

        self.callable = callable  # could be a callable, or a NodeModel. result cached in self.data
        self.name = name or callable.__name__ if callable else self.__class__.__name__
        self.continue_on_error = False  # warning or error. stop or continue the node flow on exception
        self.raise_exception = raise_exception  # debugging

    def start(self, *args, **kwargs):
        """
        starts the pipeline. call this node, then start the next node, until finished or exception
        passes args and kwargs to all callables/nodes
        """
        self(*args, **kwargs)
        if self.OUT:
            self.OUT.start(*args, **kwargs)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key == "OUT":
            # if provided None with a node stored, reset it, and reset the connection on the node
            if value is None and self.OUT:
                self.OUT.IN = None
                self.OUT = None
                return

            # assume it's a node and create a bidirectional link
            if value:
                value.IN = self



    def __gt__(self, other):
        # link nodes
        print("linking", self, other)
        self.OUT = other
        return other


    def __call__(self, *args, **kwargs) -> "typing.Any":  # protected method
        # check if all input nodes have run
        for node in self.iter_input_nodes():
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
                print(f"Failed to run {self.name}: {e}")
                raise e
            else:
                logging.error(f"Failed to run {self.name}: {e}")
            return

    # @classmethod
    # def from_module(cls, module: "str|types.ModuleType", method_name=None) -> "ProcessNode":
    #     """
    #     create a ProcessNode from a module with method'
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
    ) -> "ProcessNode":  # todo can we combine module & method_name kwarg
        """create a ProcessNode from a module with method 'main'"""
        method_name = method_name or 'main'
        callable = getattr(module, method_name)
        n = cls(callable)
        n.name = f"{module.__name__}.{method_name}"  # module + method name
        return n

    @classmethod
    def iter_nodes_from_submodules(cls, parent_module) -> "typing.Generator[ProcessNode]":
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
