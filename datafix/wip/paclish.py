# TODO pyblish adapter for datafix
# at, we just compare datafix and pyblish
import datafix
import pyblish.util

from datafix.core import Session, Collector


# ======== PAC ================================================================
class CollectHelloWorld(Collector):
    def collect(self):
        return ["Hello World"]


class CollectHelloWorld2(Collector):
    def collect(self):
        return ["Hello World2"]


# TODO helper func session.add_collector(function=CollectHelloWorld)

# setup and run session
session = Session()
session.append(CollectHelloWorld)
session.append(CollectHelloWorld2)
session.run()


# ======== PYBLISH ================================================================
class CollectHelloWorldPyblish(datafix.core.collector.Collector):
    def process(self, context):
        asset = context.create_asset('HelloWorld', family="string")
        asset[:] = ["Hello World"]


class CollectHelloWorldPyblish2(datafix.core.collector.Collector):
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
