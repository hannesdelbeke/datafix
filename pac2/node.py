import typing
from enum import Enum
import copy
import logging


# default nodes are data nodes, which contain data
class Node:
    """
    a Node contains data or callable
    a Node (output) can be connected to other Node attributes (input)
    """

    _nodes = {}  # store all nodes, to check for unique id

    # inspiration https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-map-state.html
    # success could be 0, everything else is a failure/warning ...
    class State(Enum):
        # pre run states
        INIT = "initialized"  # not run
        DISABLED = "disabled"
        # run states
        RUNNING = "running"  # run and running / in progress
        # PAUSED = "paused"
        # post run states
        SUCCEED = "succeed"  # run and success, match AWS
        FAIL = "exception"  # run and exception, match AWS
        # STOPPED = "stopped"
        # SKIPPED = "skipped"
        # PASS
        # WAIT
        # CHOICE

    def __init__(self, parent=None, data=None, name=None, state=None, id=None, children=None):

        #  --- CONNECTIONS ---
        # if we add a new node type attribute, add it to __getattribute__
        self.__output_links = {}  # when node is an input node for another node, dict with {attr name: node, ...}

        self.__children = children or []  # nodes created by this node, this is a type of connection
        self.__parent = parent  # node that created this node, this is a type of connection
        if parent:  # init parents children
            parent.children.append(self)

        # id module + name
        self.name = name or self.__class__.__name__
        self.id = id or self.__unique_id(name=name)
        self.data = data  # data (like int, str, array,...) or settings for a processNode

        # actions need a name, and a callable. not just a method.
        # actions are optional.
        # actions are nodes that run on another node
        # self.actions = []  # callables or other nodes, actions to run on this node, same as callable attributes? call/run is an action too

        self._nodes[self.id] = self  # store all nodes, to check for unique id
        self.runtime_connections = set()  # nodes used by this node during runtime, indirectly in callables

        # set init state at the end, so we can query if the init has finished.
        self.state = state or Node.State.INIT  # todo convert str to enum

    def __unique_id(self, name):
        name = name or ""
        node_path = f"{self.__class__.__module__}.{self.__class__.__name__}.{name}"  # e.g. pac2.node.Node.hello
        # if node_path in Node._nodes:  # todo check if id is unique, ensure unique
        #     # add number to end of id
        #     i = 1
        return node_path

    @property
    def children(self) -> "typing.List[Node]":
        return self.__children

    @children.setter
    def children(self, value: "typing.List[Node]"):
        # check if a list of nodes
        if not isinstance(value, list):
            raise TypeError(f"Children must be a list of Nodes, not '{type(value)}'")

        # check all values in list are nodes
        for child in value:
            if not isinstance(child, Node):
                raise TypeError(f"Children must be a list of Nodes, not '{type(child)}'")

        # disconnect from previous children
        for child in self.__children:
            child.parent = None

        # connect to new children
        self.__children = value
        for child in value:
            child.parent = self

    @property
    def parent(self) -> "typing.Optional[Node]":
        return self.__parent

    @parent.setter
    def parent(self, value: "typing.Optional[Node]"):

        # double check if value is a node
        if value is not None and not isinstance(value, Node):
            raise TypeError(f"Parent must be a 'Node' or 'None', not '{type(value)}'")

        # disconnect from previous parent
        if self.__parent:
            self.__parent.children.remove(self)

        # connect to new parent
        self.__parent = value
        if value is not None:
            value.children.append(self)

    def output(self) -> "typing.Any":  # run py code
        """returns the stored data, or the callable output if it's a ProcessNode"""
        return self.data

    def __getattribute__(self, item) -> "typing.Any":

        # todo this only triggers for attributes, not for indirect attributes like self.data.attr_name
        #  also not handling iterables yet, and deep level iters.
        #  also how to avoid triggering a generator, when you check the value is a node

        value = super().__getattribute__(item)

        if item in ("state"):
            return value
        finished_init = hasattr(self, "state")

        if callable(value) and item != "__class__" and finished_init:

            import inspect

            frames = inspect.stack()
            # i = 0
            # search the callstack for the first Node
            for f in frames:
                caller_frame = f.frame.f_back
                if not caller_frame:
                    continue

                caller_object = caller_frame.f_locals.get("self")

                if isinstance(caller_object, Node) and caller_object != self:
                    # print("caller_object", caller_object.id, "is calling self", self.id, "level", i)
                    # todo also save method name / attr where the node is used
                    self.runtime_connections.add(caller_object)
                    caller_object.runtime_connections.add(self)
                    # i += 1
                    break  # only save "direct" caller

        # if value is a Node, run it and return the result
        # exception for __class__ attr which always is of type Node
        # doesnt work for .parent, where you want to get the node, not the output. Same with children and output_links
        if isinstance(value, Node) and item not in (
            "__class__",
            "_Node__parent",
            "_Node__output_links",
            "_Node__children",
            "parent",
            "output_links",
            "children",
            "output",
            "callable",
        ):
            print(f"running node {value.name} from {self.id} for item {item}")
            value = value.output()

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
        for attr, value in self.__dict__.items():
            if callable(value):
                continue
            if attr in ("input_nodes", "connected_nodes"):  # skip method that runs this method
                continue
            if isinstance(value, Node):
                yield value

            # todo avoid triggering a generator, when you check the value is a node
            #  might be unwanted
            # check list, set, dict, ...
            try:
                for item in value:
                    if isinstance(item, Node):
                        yield item
            except TypeError:
                pass

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
        #             dct[attr_name] = value.output()
        #         # else:
        #         #     dct[attr_name] = None
        #         # edges.append((self.id, attr_name, value.id))
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

        config["root"] = self.id

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
                    edges.append((node.id, attr_name, value.id))

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
                node = cls._nodes.get(node_config["id"])

            if node.id == root_id:
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
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, Node):
                yield attr

        if recursive and hasattr(module, '__path__'):
            import importlib
            import pkgutil

            for loader, submodule_name, is_pkg in pkgutil.walk_packages(module.__path__, module.__name__ + '.'):
                spec = importlib.util.find_spec(submodule_name)
                if spec is None:
                    continue
                submodule = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(submodule)
                for _cls in cls.collect_node_classes_from_module(
                    submodule, recursive=False
                ):  # recusrive false because walk_packages is already recursive
                    # check node is not just imported in the module, but actually defined in the module
                    if "pac2.node" in _cls.__module__:
                        continue
                    yield _cls

    @classmethod
    def create_nodes_from_module(cls, module, recursive=True) -> "typing.Generator[Node]":
        """create nodes from all Node classes in a module"""
        for node_class in cls.collect_node_classes_from_module(module, recursive=recursive):
            node = node_class()
            yield node


# def collector():
# wrap collector method in node


class ProcessNode(Node):
    def __init__(self, callable=None, raise_exception=False, name=None, *args, **kwargs):
        """
        raise_exception: if True, raise exception when callable fails, else node saves exception in self.state. used for debugging
        """
        super().__init__(*args, **kwargs)
        self.callable = callable
        self.name = name or callable.__name__ if callable else self.__class__.__name__
        self.continue_on_error = False  # warning or error
        self.raise_exception = raise_exception

    def output(self, *args, **kwargs) -> "typing.Any":  # protected method
        if self.state == Node.State.DISABLED:
            return
        try:
            self.state = Node.State.RUNNING
            result = self.callable(*args, **kwargs)  # todo does this pass self?
            self.state = Node.State.SUCCEED
            self.data = result  # todo choose if we use data to cache result, or if we use it for settings. e.g. which tri-count to validate against
            return result
        except Exception as e:
            self.state = Node.State.FAIL
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
    #     import importlib
    #
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
        import pkgutil
        import importlib

        for module_info, name, is_pkg in list(pkgutil.iter_modules(parent_module.__path__)):
            spec = module_info.find_spec(name)
            module = importlib.util.module_from_spec(spec)
            module = importlib.import_module(f'{parent_module.__name__}.{module.__name__}')

            node = cls.node_from_module(module)
            yield node


def import_module_from_path(module_path) -> "types.ModuleType|None":
    import importlib.util

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

    def output(self):  # todo
        if self.validation_node.state == Node.State.DISABLED:
            return

        for node in self.iter_input_nodes():
            if self.validation_node.state == Node.State.FAIL:
                self.state = Node.State.FAIL
                return  # todo stop or continue on fail

            self.validation_node.output(node)
            if node.state != Node.State.SUCCEED:
                self.state = Node.State.FAIL
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
