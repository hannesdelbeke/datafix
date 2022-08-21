import pac.orders.pyblish

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


class Node(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.children = []
        self.state = 'uninitialized'
        self.connections = []  # indirect connections, excl parent

    # run on fail yes/no
    # dependencies/requires

    pass


class Action(object):
    # TODO add connection when run on node

    # an action is just a function with a name?

    # def print_hello():
    #     print("Hello World")
    # action = Action(function=print_hello, 'print_hello')
    #
    # action = Action()
    # action.function = print_hello
    # action.name = 'print_hello'

    def __init__(self, function=None, name=None):
        self.function = function
        self.name = name

    # node could be session, or could be instance
    def run(self, node, *args, **kwargs):
        # TODO check if function takes args and kwargs
        self.function(node, *args, **kwargs)


class Collector(Node):  # session plugin (context), session is a node
    order = pac.orders.pyblish.COLLECT

    @property
    def instance_wrappers(self):
        return self.children

    def __init__(self, parent):
        self.actions = []
        super().__init__(parent=parent)

    def run(self):
        # returns for example meshes, or strings
        raise NotImplementedError()

    def _run(self, session):  # create instances node(s)
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


# get all instances from session (from collectors) from type X (mesh) and validate
class Validator(Node): # instance plugin
    order = pac.orders.pyblish.VALIDATE

    def __init__(self, parent):
        self.actions = []
        super().__init__(parent=parent)

    def run(self, instance):
        raise NotImplementedError()

    # get the collect instances from session, get the mesh instances from collect instances,
    # run validate on the mesh instances, create backward link (to validate inst) in mesh instances
    def _run(self, session):  # create instances node(s)
        try:
            # get matching instances from session
            for plugin_instance in session.plugin_instances:
                for instance_wrap in plugin_instance.children:

                    self.connections.append(instance_wrap)
                    instance_wrap.connections.append(self)

                    try:
                        self.state = 'running'
                        result = self.run(instance=instance_wrap.instance)
                        self.state = 'success'
                    except:
                        self.state = 'failed'
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

    def run(self):
        for plugin_class in self.registered_plugins:
            print("running", plugin_class)
            plugin_instance = plugin_class(parent=self)
            self.plugin_instances.append(plugin_instance)
            plugin_instance._run(session=self)

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
