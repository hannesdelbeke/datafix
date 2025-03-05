"""
the discover module is not used atm
"""

import importlib
import pkgutil

import datafix
import pprint


def discover_modules():
    """
    Discover all datafix plugin modules.
    To make your module discoverable by datafix, it must be in a folder named pac_plugins,
    and included in your python path.
    """
    discovered_modules = {}
    for finder, name, ispkg in pkgutil.walk_packages():
        if 'pac_plugins' not in name:
            continue
        try:
            discovered_modules[name] = (importlib.import_module(name), ispkg)
        except Exception as e:
            print(f"Failed to import module {name}. {e}")
    return discovered_modules


def discover_plugins():
    """
    go over discovered modules and check for classes that inherit from Plugin
    return list of plugins
    """
    discovered_modules = discover_modules()
    discovered_plugins = set()
    for name, (module, ispkg) in discovered_modules.items():
        for attr_name in dir(module):

            # skip private classes
            if attr_name.startswith('_'):
                continue

            # check for Node class
            attr = getattr(module, attr_name)
            try:
                if not issubclass(attr, datafix.Node.Node):
                    continue
            except TypeError:
                continue

            # to ensure the same class is not included twice,
            # we need to check if the class is already in the set
            # but a simple comparison will not work
            # because the class is not the same object
            # so we need to compare the class name, and module name
            # if the class is already in the set, we skip it
            already_registered = False
            for registered_node in discovered_plugins:
                same_module = importlib.import_module(registered_node.__module__).__file__ == module.__file__
                same_name = registered_node.__name__ == attr.__name__
                if same_module and same_name:
                    already_registered = True
                    break
            if not already_registered:
                discovered_plugins.add(attr)

    return discovered_plugins


# discover all datafix plugins and print them
if __name__ == '__main__':
    pprint.pprint(discover_plugins())
