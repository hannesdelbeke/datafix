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

class Node(object):
    def __init__(self, parent=None, name=None):
        # self.action_class = None
        # self.action = None

        self.parent = parent  # node that created this node
        self.children = []  # nodes created by this node
        self.connections = []  # related nodes

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
        try:
            self.state = 'running'
            result = self._run()
            self.state = 'success'
            return result
        except Exception as e:
            self.state = 'failed'
            print(e)

    def pp_tree(self, depth=0):
        """
        Session ==>> initialized
          CollectHelloWorld ==>> success
            InstanceWrapper (Hello World)==>> initialized
          CollectHelloWorldList ==>> success
            InstanceWrapper (Hello)==>> initialized
            InstanceWrapper (World)==>> initialized
          ValidateHelloWorld ==>> failed
        """
        txt = '  '*depth + self.__class__.__name__ + ' ==>> ' + self.state + '\n'
        for child in self.children:
            try:
                txt += child.pp_tree(depth=depth+1).replace('==>>', f'({child.instance})==>>')
            except AttributeError:
                txt += child.pp_tree(depth=depth+1)
        if depth == 0:
            print(txt)
        return txt


class Action(Node):
    # TODO add connection when run on node

    # an action is just a function with a name?

    # def print_hello():
    #     print("Hello World")
    # action = Action(function=print_hello, 'print_hello')
    #
    # action = Action()
    # action.function = print_hello
    # action.name = 'print_hello'

    def __init__(self, parent, function=None, name=None):
        # parent, whatever initiated this action
        self.function = function
        self.state = 'not run'
        super().__init__(parent=parent, name=name)

    # node could be session or instance or collector or validator
    def _run(self, *args, **kwargs):
        """node is the parent of this action"""
        # TODO check if function takes args and kwargs
        # either wrap function or inherit action and overwrite run
        parent_node = self.parent
        self.function(parent_node, *args, **kwargs)

    def _run(self):  # create instances node(s)
        try:
            self.state = 'running'

            result = self.run()

            for instance in result:
                wrap = InstanceWrapper(instance, parent=self)
                self.instance_wrappers.append(wrap)

            self.state = 'success'

        # if not implemented, return empty list
        except NotImplementedError:
            result = []
            print('Not implemented', self)


# class ActionCollect(Action):
#     def _run(self):  # create instances node(s)
#         print(self._run)
#         try:
#             self.state = 'running'
#
#             result = self.run()
#
#             for instance in result:
#                 wrap = InstanceWrapper(instance, parent=self)
#                 self.parent.instance_wrappers.append(wrap)
#
#             self.state = 'success'
#
#         # if not implemented, return empty list
#         except NotImplementedError:
#             result = []


class Collector(Node):  # session plugin (context), session is a node
    @property
    def instance_wrappers(self):
        return self.children

    # def collect(self):
    #     raise NotImplementedError

    def run(self):
        result = super().run()

        for instance in result:
            wrap = InstanceWrapper(instance, parent=self)
            self.instance_wrappers.append(wrap)

        return result

    def _run(self):  # create instances node(s)
        raise NotImplementedError
        # print(self._run)
        # # if self.action_class:
        #     # self.action = self.action_class(parent=self)
        #     # result = self.action._run()
        #
        # # result = self.run()
        # result = self.collect()
        #
        # for instance in result:
        #     wrap = InstanceWrapper(instance, parent=self)
        #     self.instance_wrappers.append(wrap)
        #
        # return result


# get all instances from session (from collectors) from type X (mesh) and validate
class Validator(Node):  # instance plugin
    def validate_instance(self, instance):
        raise NotImplementedError()

    # get the collect instances from session, get the mesh instances from collect instances,
    # run validate on the mesh instances, create backward link (to validate inst) in mesh instances
    def _run(self):  # create instances node(s)
        try:
            # get matching instances from session
            for plugin_instance in self.session.plugin_instances:
                for instance_wrap in plugin_instance.children:

                    self.connections.append(instance_wrap)
                    instance_wrap.connections.append(self)

                    try:
                        instance_wrap.state = 'running'
                        result = self.validate_instance(instance=instance_wrap.instance)
                        instance_wrap.state = 'success'
                    except:
                        instance_wrap.state = 'failed'
                    print("validate " + self.state, instance_wrap.instance)
        # if not implemented, return empty list
        except NotImplementedError:
            print('failed')
            pass


# make this generic CICD / super simple.
# then marketplace with premade packages/plugins
# language agnostic ideally

class Session(Node):
    def __init__(self):
        self.registered_plugins = []
        super().__init__()

    @property
    def plugin_instances(self):
        return self.children

    # @property
    # def collected_instances(self):
    #     return self.children

    def run(self):
        for plugin_class in self.registered_plugins:
            print("running", plugin_class)
            plugin_instance = plugin_class(parent=self)
            self.plugin_instances.append(plugin_instance)
            # print("running", plugin_instance)
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

class InstanceWrapper(Node):
    """
    instance wrapper can only contain 1 instance. But an instance can be a list of data
    """
    def __init__(self, instance, parent):
        # self.actions = []
        self.instance = instance
        super().__init__(parent=parent)

    def __str__(self):
        return f'InstanceWrapper({self.instance})'

    def __repr__(self):
        return f'InstanceWrapper({self.instance})'
