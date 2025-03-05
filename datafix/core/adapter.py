# session
#  collect_node
#    instance_wrap A
#      instance A
#    instance_wrap B
#      instance B
#  validator_node
#    get session, get plugins with instances(aka children)
#    run an action on each instance, result SUCCESS or FAIL (or WARNING/ custom)
# action can be attached and run on every node (right click in UI)
# repair/fix can use these actions
# validate node is an action, get the instance wrapper children and validate them

# create collect n validation plugins
# add fix action

# register UI
# register maya
# register collector
# register validator

# test this with the RPM pipeline
# import bpy


# ypu  cant run a node, you can run an action on a node
# nodes contain data and connections, and connect to action_nodes and instances
# action nodes can be run
# instances contain data like meshes, strings, ...

# from datafix.node import Node, NodeState
# from datafix.session import Session
# from datafix.validator import Validator
# from datafix.collector import Collector
# from datafix.datanode import DataNode
# from datafix.resultnode import ResultNode


class Adapter:
    # when we run on another node, sometimes we expect input of a certain type.
    # this is the adapter class, which can convert the input to the expected type
    # if there is a registered adapter

    type_input = None
    type_output = None

    def adapt(self, data):
        """the logic that adapts the data to another type, override this"""
        raise NotImplementedError()

    def run(self, data):
        return self.adapt(data)

    # input: instance(wrapper?)
    # output: int


# class AdapterBrain(object):
#     def __init__(self):



