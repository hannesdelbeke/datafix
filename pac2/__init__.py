class Node:
    def __init__(self, parent=None):
        self.name = self.__class__.__name__
        self.parent = parent
        self.children = []
        if parent and self not in parent.children:
            parent.children.append(self)

    def run(self):
        pass


# def collector():
# wrap collector method in node


class MethodWrapperNode(Node):
    def __init__(self, callable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._callable = callable
        self.name = callable.__name__

    def run(self):
        return self.method()

    def __repr__(self):
        return f"Node({self.name})"


def import_module_from_path(module_path):
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


def create_node_from_module(module, method_name=None):
    """create a node from a module with method 'main'"""
    method_name = method_name or 'main'
    n = MethodWrapperNode(module.main)
    n.name = f"{module.__name__}.{method_name}"  # module + method name
    return n


# def import_module_from_path(path):
#     import pkgutil
#     import importlib
#
#     module_info, name, is_pkg = list(pkgutil.iter_modules(path))[0]
#     spec = module_info.find_spec(name)
#     module = importlib.util.module_from_spec(spec)
#     # todo parent_module
#     module = importlib.import_module(f'{parent_module.__name__}.{module.__name__}')


def nodes_from_submodules(parent_module):
    """create nodes from all submodules in a module"""
    import pkgutil
    import importlib

    for module_info, name, is_pkg in list(pkgutil.iter_modules(parent_module.__path__)):
        spec = module_info.find_spec(name)
        module = importlib.util.module_from_spec(spec)
        module = importlib.import_module(f'{parent_module.__name__}.{module.__name__}')

        node = create_node_from_module(module)
        yield node


def get_node_tree():
    import pac2.validators.deepnest

    parent_module = pac2.validators.deepnest
    nodes = list(nodes_from_submodules(parent_module))
    return nodes


if __name__ == '__main__':
    from pac2.my_module import mesh_collection

    n = MethodWrapperNode(mesh_collection)
    print(n)
    print(n.name)

    n = MethodWrapperNode(lambda x: 1)
    print(n)
    print(n.name)

    nodes = get_node_tree()
    print(nodes)
