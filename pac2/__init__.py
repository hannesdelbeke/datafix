import typing
from enum import Enum


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


class Node:
    # __slots__ =  ... could set slots for performance
    def __init__(self, parent=None):
        self.name = self.__class__.__name__
        self.parent = parent
        self.children = []
        self.state = NodeState.INIT
        if parent and self not in parent.children:
            parent.children.append(self)

    def eval(self):
        pass


# def collector():
# wrap collector method in node


class DataNode(Node):
    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data

    def eval(self):
        return self.data


class ProcessNode(Node):
    def __init__(self, callable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._callable = callable
        self.name = callable.__name__
        self.allow_failure = False  # warning or error

    def eval(self) -> "typing.Any":
        try:
            result = self.method()
            self.state = NodeState.SUCCEED
        except Exception as e:
            self.state = NodeState.FAIL
            result = None
            print(f"Error: {e}")
        return result

    def __repr__(self):
        return f"Node({self.name})"

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


def get_node_tree():
    import pac2.validators.deepnest

    parent_module = pac2.validators.deepnest
    nodes = list(ProcessNode.iter_nodes_from_submodules(parent_module))
    return nodes


if __name__ == '__main__':
    from pac2.my_module import mesh_collection

    nodes = get_node_tree()
    print(nodes)

    # a = object()
    # b = 2
    # print(Node().name)
    # print(dir(get_node_tree))
    # print(dir(a))
    # print(dir(b))
