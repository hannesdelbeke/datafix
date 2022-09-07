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


# class AdapterBrain(object):
#     def __init__(self):


class Adapter(object):
    # when we run on another node, sometimes we expect input of a certain type.
    # this is the adapter class, which can convert the input to the expected type
    # if there is a registered adapter

    type_input = None
    type_output = None

    def _run(self, instance):
        raise NotImplementedError()

    def run(self, instance):
        return self._run(instance)

    # input: instance(wrapper?)
    # output: int


class Node(object):
    def __init__(self, parent=None, name=None):
        # self.action_class = None
        self.actions = []
        self.result = None  # run result # TODO ensure this can be identified as not run yet? combine w state?
        self.results = []

        self.parent = parent  # node that created this node
        self.children = []  # nodes created by this node
        self.connections = []  # related nodes
        # TODO instead of storing result in 1 node, and then quering this node from the other node for the result.
        #  we can store the result in the link/connection between nodes

        self.state = 'initialized'
        # self.name = name

    @property
    def session(self):
        if self.parent:
            return self.parent.session
        else:
            return self

    def _run(self):
        """
        inherit and overwrite this
        """
        raise NotImplementedError

    def run(self):
        """
        public method, don't overwrite this
        """
        result = None
        try:
            self.state = NodeState.RUNNING
            result = self._run()
            self.state = NodeState.SUCCEED
        except Exception as e:
            self.state = NodeState.FAIL
            print(e)

        # self.results.append(self.state)
        self.result = result

        return result

    def pp_tree(self, depth=0):
        """
        Session ==>> initialized
          CollectHelloWorld ==>> succeed
            InstanceWrapper (Hello World)==>> initialized
          CollectHelloWorldList ==>> succeed
            InstanceWrapper (Hello)==>> initialized
            InstanceWrapper (World)==>> initialized
          ValidateHelloWorld ==>> failed
        """
        txt = '  ' * depth + self.__class__.__name__ + ' ==>> ' + str(self.state) + '\n'
        for child in self.children:
            try:
                txt += child.pp_tree(depth=depth + 1).replace('==>>', f'({child.instance})==>>')
            except AttributeError:
                txt += child.pp_tree(depth=depth + 1)
        if depth == 0:
            print(txt)
        return txt


class Action(Node):
    pass


class Collector(Node):  # session plugin (context), session is a node
    @property
    def instance_wrappers(self):
        return self.children

    def run(self):
        result = super().run()

        for instance in result:
            wrap = InstanceWrapper(instance, parent=self)
            self.instance_wrappers.append(wrap)

        return result

    def _run(self):  # create instances node(s)
        raise NotImplementedError


# get all instances from session (from collectors) from type X (mesh) and validate
class Validator(Node):  # instance plugin
    required_type = None

    def __init__(self, parent):
        super().__init__(parent=parent)
        # self.results = []  # store run stuff in here
        # self.required_type = None  # type of instance to validate

    def _validate_instance(self, instance):
        instance = self.session.adapt(instance, self.required_type)
        return self.validate_instance(instance)

    def validate_instance(self, instance):
        raise NotImplementedError()

    # overwrite this one! no automated adapter though
    def _validate_instance_wrapper(self, instance_wrapper):
        return self._validate_instance(instance=instance_wrapper.instance)

    # public func, dont overwrite
    def validate_instance_wrapper(self, instance_wrapper):
        self.connections.append(instance_wrapper)
        instance_wrapper.connections.append(self)
        try:
            state = NodeState.RUNNING
            result = self._validate_instance_wrapper(instance_wrapper=instance_wrapper)
            state = NodeState.SUCCEED
        except Exception as e:
            print(e)
            state = NodeState.FAIL
        self.results.append([instance_wrapper, state])

    # get the collect instances from session, get the mesh instances from collect instances,
    # run validate on the mesh instances, create backward link (to validate inst) in mesh instances
    def _run(self):  # create instances node(s)
        try:
            self.results = []
            # get matching instances from session
            for plugin_instance in self.session.plugin_instances:
                for instance_wrap in plugin_instance.children:
                    self.validate_instance_wrapper(instance_wrap)

        # if not implemented, return empty list
        except NotImplementedError:
            print('NotImplementedError')
            pass


# make this generic CICD / super simple.
# then marketplace with premade packages/plugins
# language agnostic ideally


class Session(Node):
    def __init__(self):
        self.registered_plugins = []
        self.registered_adapters = []
        super().__init__()

    @property
    def plugin_instances(self):
        return self.children

    # @property
    # def collected_instances(self):
    #     return self.children

    def run(self):
        for plugin_class in self.registered_plugins:
            plugin_instance = plugin_class(parent=self)
            self.plugin_instances.append(plugin_instance)
            plugin_instance.run()

        # create collector instance and track in session, create backward link in collect instance
        # collector.run(session)
        # store mesh instances in the collector instance, create backward link in mesh instances

        # create validator instance and track in session, create backward link in validator instance
        # validator.run(session)
        # get the collect instances from session, get the mesh instances from collect instances,
        # run validate on the mesh instances, create backward link (to validate inst) in mesh instances

        # create export instance and track in session, create backward link in export instance
        # export.run(session)
        # get the collect instances from session, get mesh inst from collect inst.
        # run export on the mesh instances, create backward link (to export inst) in mesh instances

    def adapt(self, instance, required_type):
        if not required_type:
            return instance

        if required_type == type(instance):
            return instance

        for adapter in self.registered_adapters:
            if adapter.type_output == required_type and adapter.type_input == type(instance):
                return adapter.run(instance)
        return None

    def register_adapter(self, adapter):
        self.registered_adapters.append(adapter)


class InstanceWrapper(Node):
    """
    instance wrapper can only contain 1 instance. But an instance can be a list of data
    """

    def __init__(self, instance, parent):
        # self.actions = []
        self.instance = instance
        super().__init__(parent=parent)

    @property
    def state(self):

        # other nodes, ex validator, ran on an instance node.
        # we collect the results of the nodes and return fail if any of them failed

        state = NodeState.SUCCEED
        # TODO make this a dict
        # a connections is a node connected to 2 nodes
        # a connection can contain data.

        for node in self.connections:
            for result_node, result_state in node.results:
                if result_node != self:
                    continue
                if result_state == NodeState.FAIL:
                    state = NodeState.FAIL
                    return state
            # if node == self:
            #     return state
        return state

    @state.setter
    def state(self, state):
        pass

    def __str__(self):
        return f'InstanceWrapper({self.instance})'

    def __repr__(self):
        return f'InstanceWrapper({self.instance})'
