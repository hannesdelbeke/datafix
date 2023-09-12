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

    _nodes = {}  # store all nodes, to check for unqiue id

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

    def __unique_id(self, name):
        name = name or ""
        node_path = f"{self.__class__.__module__}.{self.__class__.__name__}.{name}"  # e.g. pac2.node.Node.hello
        # if node_path in Node._nodes:  # todo check if id is unique, ensure unique
        #     # add number to end of id
        #     i = 1
        return node_path

    def __init__(self, parent=None, data=None, name=None):

        #  --- CONNECTIONS ---
        # if we add a new node type attribute, add it to __getattribute__
        self.__children = []  # nodes created by this node, this is a type of connection
        self.__output_links = {}  # when node is an input node for another node, dict with {attr name: node, ...}
        self.__parent = parent  # node that created this node, this is a type of connection
        if parent:  # init parents children
            parent.children.append(self)

        # id module + name
        self.name = name or self.__class__.__name__ or ""  # __name__
        self.id = self.__unique_id(name=name)
        self.state = Node.State.INIT
        self.data = data  # data (like int, str, array,...) or settings for a processNode
        # self.actions = []  # callables or other nodes, actions to run on this node, same as callable attributes? call/run is an action too

    @property
    def children(self):
        return self.__children

    @children.setter
    def children(self, value):
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
    def parent(self, value):

        # double check if value is a node
        if value is not None and not isinstance(value, Node):
            raise TypeError(f"Parent must be a Node, not '{type(value)}'")

        # disconnect from previous parent
        if self.__parent:
            self.__parent.children.remove(self)

        # connect to new parent
        self.__parent = value
        if value:
            value.children.append(self)

    # def __delattr__(self, item):
    #     print("del attr", item)
    #     super().__delattr__(item)

    # def __del__(self):
    #     # cleanup connections before deleting
    #     # todo de we also delete the children?
    #     # disconnect children
    #     # import traceback
    #     # traceback.print_stack()
    #
    #     print("del", type(self))
    #
    #
    #     for child in self.children:
    #         print(self.children)
    #         # try:
    #         print(type(child))
    #         print(child.name)
    #         child.parent = None
    #         # except AttributeError:
    #         #     logging.warning(f"Failed to disconnect child {child} from parent {self}")
    #
    #     # remove self from parent
    #     if self.parent:
    #         # try:
    #         self.parent.children.remove(self)
    #         # except AttributeError:
    #         #     logging.warning(f"Failed to disconnect parent {self.parent} from child {self}")
    #
    #     # remove self from nodes
    #     if self.id in Node._nodes:
    #         del Node._nodes[self.id]
    #
    #     # get all output links and set attr to none
    #     for attr, node in self.__output_links.items():
    #         setattr(node, attr, None)

    def output(self) -> "typing.Any":  # run py code
        """returns the stored data, or the callable output if it's a ProcessNode"""
        return self.data

    def __getattribute__(self, item) -> "typing.Any":
        value = super().__getattribute__(item)

        # if value is a Node, run it and return the result
        # exception for __class__ attr which always is of type Node
        # todo doesnt work for .parent, where you want to get the node, not the output. Same with children and output_links
        if isinstance(value, Node) and item not in (
            "__class__",
            "_Node__parent",
            "_Node__output_links",
            "_Node__children",
            "parent",
            "output_links",
            "children",
        ):  # , "__parent", "parent", "children", "output_links"):
            value = value.output()

        return value

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)

        # don't track if it's a property, else attributes are duplicated in the '.__output_links ' dict
        # {'_Node__parent': Node(b), 'parent': Node(b)}
        if key not in self.__dict__:
            return

        # track connected nodes
        if isinstance(value, Node):
            value.__output_links[key] = self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"  # e.g. Node(hello)

    def iter_value_attrs(self) -> "typing.Generator[typing.Tuple[str, typing.Any]]":
        """iterate over all attributes that are not callable"""
        # for attr in dir(self):
        for attr, value in self.__dict__.items():
            if attr in ("input_nodes", "connected_nodes"):  # skip method that runs this method
                continue
            # value = getattr(self, attr)
            if callable(value):
                continue
            # also skip method-wrappers & built-in methods
            # if attr.startswith("__"):
            #     continue
            yield attr, value

    def iter_input_nodes(self) -> "typing.Generator[Node]":
        """iterate over all input nodes"""
        for attr, value in self.iter_value_attrs():
            if isinstance(value, Node):
                yield value

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
    def connected_nodes(self) -> "typing.List[Node]":
        """return all connected nodes"""
        return self.input_nodes + self.output_nodes

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
        dct = copy.deepcopy(self.__dict__)  # prevent mutating self.__dict__
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

        return dct

    def to_config(self, _collected_nodes=None, _config=None):
        config = _config or {}
        config["nodes"] = node_configs = config.get("nodes", [])
        config["edges"] = edges = config.get("edges", [])  # todo support edge attrs

        collected_nodes = _collected_nodes or set()

        # export node, and all connected nodes.
        for node in self.connected_nodes:

            if node in collected_nodes:
                continue
            collected_nodes.add(node)
            node.to_config(collected_nodes, config)

            # collect nodes
            node_config = node.serialize()
            node_configs.append(node_config)

            for attr_name, value in node_config.items():

                if isinstance(value, Node):
                    edges.append((node.id, attr_name, value.id))

        return config

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

    # def load_config(self, config_data, node):
    # config_data is dict

    # get all attrs, if any contains Nodes, recursive run this method on it.
    # dct = {}
    # for attr, value in self.iter_value_attrs():
    #     # value = getattr(self, attr)
    #     if isinstance(value, Node):  # todo do we need exception for __class__ ?
    #         dct[attr] = value.serialize()
    #     else:
    #         dct[attr] = value
    # return dct

    # e.g. node = Node()
    # {
    #     "name": "node",
    #     "data": None,
    #     "state": "INIT",
    #     "children": [],
    #     "parent": None,
    #     "output_links": {}
    # }

    # optimised
    # {
    #     "name": "node",
    # }

    # todo make data identify as node, e.g. with "is_node": True


# def collector():
# wrap collector method in node


class ProcessNode(Node):
    def __init__(self, callable=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callable = callable
        self.name = callable.__name__ if callable else self.__class__.__name__
        self.continue_on_error = False  # warning or error

    def output(self, *args, **kwargs) -> "typing.Any":  # protected method
        if self.state == Node.State.DISABLED:
            return
        try:
            self.state = Node.State.RUNNING
            result = self.callable(*args, **kwargs)  # todo does this pass self?
            self.state = Node.State.SUCCEED
            self.data = result
            return result
        except Exception as e:
            self.state = Node.State.FAIL
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

    # @classmethod  # todo comment out because swap to callable
    # def node_from_module(cls, module, method_name=None) -> "ProcessNode":  # todo can we combine module & method_name kwarg
    #     """create a ProcessNode from a module with method 'main'"""
    #     method_name = method_name or 'main'
    #     callable = getattr(module, method_name)
    #     n = cls(callable)
    #     n.name = f"{module.__name__}.{method_name}"  # module + method name
    #     return n

    # @classmethod
    # def iter_nodes_from_submodules(cls, parent_module) -> "typing.Generator[ProcessNode]":
    #     """create ProcessNodes generator from all submodules in a module"""
    #     import pkgutil
    #     import importlib
    #
    #     for module_info, name, is_pkg in list(pkgutil.iter_modules(parent_module.__path__)):
    #         spec = module_info.find_spec(name)
    #         module = importlib.util.module_from_spec(spec)
    #         module = importlib.import_module(f'{parent_module.__name__}.{module.__name__}')
    #
    #         node = cls.node_from_module(module)
    #         yield node


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


# def import_module_from_path(path):
#     import pkgutil
#     import importlib
#
#     module_info, name, is_pkg = list(pkgutil.iter_modules(path))[0]
#     spec = module_info.find_spec(name)
#     module = importlib.util.module_from_spec(spec)
#     # todo parent_module
#     module = importlib.import_module(f'{parent_module.__name__}.{module.__name__}')


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

if __name__ == '__main__':
    from pac2.my_module import mesh_collection

    import pac2.validators.deepnest

    # collect validations
    validate_nodes = list(ValidatorNode.iter_nodes_from_submodules(pac2.validators.deepnest))

    # val_node.input_nodes = instance_nodes
    print(validate_nodes)

    # collect instances
    strings = ["hello", "world", "hella", "hello"]
    instance_nodes = [Node(data=s) for s in strings]

    # node = DataNode(strings)  # todo good sample for adapter pattern

    # val_node = ValidatorNode(input_nodes=instance_nodes)
    # val_node.output()

    # print(val_node)
    # print(val_node.results)
    # print(val_node.linked_nodes[0].linked_nodes)

    # # validate instances
    # for instance_node in instance_nodes:
    #     for validate_node in validate_nodes:
    #         validate_node.output(instance_node)

    # validate
    # for

    # todo families / tags categories are set in config or second script. the logic/method is in sep module.

    # a = object()
    # b = 2
    # print(Node().name)
    # print(dir(get_node_tree))
    # print(dir(a))
    # print(dir(b))


def mesh_collector():
    import bpy

    return [o for o in bpy.data.objects if o.type == "MESH"]


class MeshCollector(ProcessNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def output(self):
        result = mesh_collector()
        for m in result:
            Node(data=m, parent=self)


# class NodeManager(Node):
#     # def __int__(self):
#
#     # PUBLISH (run whole pipeline)
#
#     # discover all nodes from registered paths.
#     # todo paths = [r"C:\Users\michael\Documents\GitHub\pac2\pac2\validators\deepnest.py"]
#     # user is responsible for registering paths, need to have an importable py module.
#     # helper function to add to path?
#
#     nodes = ProcessNode.iter_nodes_from_submodules(pac2.validators.deepnest)
#
#     # register (connect) all nodes to manager node
#     manager_node = ProcessNode()  # if you call it, you publish it.
#
#     # run collectors, collect data nodes, tag them with categories/families
#     # run validators (on tagged data nodes)
#
