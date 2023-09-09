import typing
from enum import Enum


# inspiration https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-map-state.html
# success could be 0, everything else is a failure/warning ...
class NodeState(Enum):
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


# default nodes are data nodes, which contain data
class Node:
    def __init__(self, parent=None, data=None, name=None):
        # self.id = None
        self.parent = parent  # node that created this node
        self.children = []  # nodes created by this node
        self.state = NodeState.INIT
        self.name = name or self.__class__.__name__  # __name__
        self.data = data
        self.__output_links = {}  # when node is an input node for another node # todo

        if parent and self not in parent.children:
            parent.children.append(self)

    def output(self):  # run py code
        return self.data

    def __getattribute__(self, item):
        value = super().__getattribute__(item)
        # if value is a Node, run it and return the result
        # exception for __class__ attr which always is of type Node
        if isinstance(value, Node) and item != "__class__":
            value = value.output()
        return value

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        # track connected nodes
        if isinstance(value, Node):
            value.__output_links[key] = self

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"  # e.g. Node(hello)

    def iter_input_nodes(self):
        for attr in dir(self):
            value = getattr(self, attr)
            if isinstance(value, Node):
                yield value

    @property
    def input_nodes(self):
        return list(self.iter_input_nodes())

    @property
    def output_nodes(self):
        return self.__output_nodes.values()

    @property
    def output_links(self):
        """return dict of output links, where key is the attribute name, and value is the node"""
        return self.__output_links


# def collector():
# wrap collector method in node


class ProcessNode(Node):
    def __init__(self, callable=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callable = callable
        self.name = callable.__name__ if callable else self.__class__.__name__
        self.continue_on_error = False  # warning or error

    def output(self, *args, **kwargs) -> "typing.Any":  # protected method
        if self.state == NodeState.DISABLED:
            return
        try:
            self.state = NodeState.RUNNING
            result = self.callable(*args, **kwargs)  # todo does this pass self?
            self.state = NodeState.SUCCEED
            return result
        except Exception as e:
            self.state = NodeState.FAIL
            print(f"Error: {e}")
            return

    @classmethod
    def node_from_module(cls, module, method_name=None) -> "ProcessNode":
        """create a ProcessNode from a module with method 'main'"""
        method_name = method_name or 'main'
        n = cls(module.main)
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
        print(f"Failed to import module from path: {module_path}")
        print(f"Error: {e}")
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

    def __init__(self, input_nodes=None, continue_on_fail=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.continue_on_fail = continue_on_fail

        # self.add_input_nodes(input_nodes or [])  # todod option to link input node to any attribute of this node

    def output(self):  # todo
        if self.validation_node.state == NodeState.DISABLED:
            return

        # todo hacky for now, make property later maybe
        for node in self.input_nodes:
            self.linked_nodes.append(node)
            node.linked_nodes.append(self)

        for node in self.input_nodes:
            if self.validation_node.state == NodeState.FAIL:
                self.state = NodeState.FAIL
                return  # todo stop or continue on fail

            self.validation_node.output(node)
            if node.state != NodeState.SUCCEED:
                self.state = NodeState.FAIL
                return

            # todo add bidirectional link to node we ran on

    # def add_input_nodes(self, nodes):  # todo link slotname node
    #     self.input_nodes.extend(nodes)
    #     for node in nodes:
    #         node.linked_nodes.append(self)

    @property
    def results(self):
        return [node.state for node in self.input_nodes]


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
