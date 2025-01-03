# TODO pyblish adapter for pac
# at, we just compare pac and pyblish

from pac.logic import *
import pyblish.api
import pyblish.util
import pprint


# ======== PAC ================================================================
class CollectHelloWorld(Collector):
    def logic(self):
        return ["Hello World"]


class CollectHelloWorld2(Collector):
    def logic(self):
        return ["Hello World2"]


# TODO helper func session.add_collector(function=CollectHelloWorld)

# setup and run session
session = Session()
session.nodes.append(CollectHelloWorld)
session.nodes.append(CollectHelloWorld2)
session.run()

# print results
session.pp_tree()


# ======== PYBLISH ================================================================
class CollectHelloWorldPyblish(pyblish.api.Collector):
    def process(self, context):
        asset = context.create_asset('HelloWorld', family="string")
        asset[:] = ["Hello World"]


class CollectHelloWorldPyblish2(pyblish.api.Collector):
    def process(self, context):
        asset = context.create_asset('HelloWorld2', family="string")
        asset[:] = ["Hello World2"]


# setup and run session
pyblish.api.deregister_all_paths()
pyblish.api.register_plugin(CollectHelloWorldPyblish)
pyblish.api.register_plugin(CollectHelloWorldPyblish2)
context = pyblish.util.publish()

# print results
print(type(context))
plugin: pyblish.api.Plugin
for inst in context:
    print('  ', inst, type(inst))
