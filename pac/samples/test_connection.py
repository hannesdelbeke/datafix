from pac.port import *

# session
#   collect_node
#     instance A
#     instance B
#   validator_node
#     validate A SUCCESS
#     validate B FAIL

# connection instance A -> validator A, result SUCCESS
# connection instance B -> validator A, result FAIL


class CollecA(Collector):
    def run(self):
        return ["A"]


class CollecB(Collector):
    def run(self):
        return ["B"]


class ValidatorAB(Validator):
    def run(self, instance):
        assert instance == "A"


session = Session()
session.registered_plugins.append(CollecA)
session.registered_plugins.append(CollecB)
session.registered_plugins.append(ValidatorAB)
session.run()

# running <class '__main__.CollecA'>
# running <class '__main__.CollecB'>
# running <class '__main__.ValidatorAB'>
# validate success A
# validate failed B


# query result from instance A
collect_a_plugin_inst = session.plugin_instances[0]
instance_wrap_a = collect_a_plugin_inst.children[0]
print()
print(instance_wrap_a)
print(instance_wrap_a.parent)
print(instance_wrap_a.parent.state)
print(instance_wrap_a.connections)
print(instance_wrap_a.connections[0].state)

# InstanceWrapper(A)
# <__main__.CollecA object at 0x0000010AA57F3D00>
# success
# [<__main__.ValidatorAB object at 0x0000016ECDADE370>]
