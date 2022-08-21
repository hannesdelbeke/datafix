import orders.pyblish

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
        self.instances = []
        self.state = 'uninitialized'


    # run on fail yes/no
    # dependencies/requires

    pass



class Action(object):
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
    order = orders.pyblish.COLLECT

    def __init__(self, parent):
        self.instances = []
        self.actions = []
        super().__init__(parent=parent)

    def run(self):
        # returns for example meshes, or strings
        raise NotImplementedError()

    def _run(self, session):  # create instances node(s)
        try:
            result = self.run()

            for instance in result:
                wrap = InstanceWrapper(instance, parent=self)
                self.instances.append(wrap)

            # wrap result in instance
            # add to session
            # add to self.instances
            self.instances


        # if not implemented, return empty list
        except NotImplementedError:
            result = []


# get all instances from session (from collectors) from type X (mesh) and validate
class Validator(Node): # instance plugin
    order = orders.pyblish.VALIDATE

    def __init__(self, parent):
        self.instances = []
        self.actions = []
        super().__init__(parent=parent)

    def run(self, instance):
        raise NotImplementedError()

    # get the collect instances from session, get the mesh instances from collect instances,
    # run validate on the mesh instances, create backward link (to validate inst) in mesh instances
    def _run(self, session):  # create instances node(s)
        print("validating")
        try:
            # get matching instances from session
            for plugin_instance in session.instances:
                for instance_wrap in plugin_instance.instances:
                    print("validating", instance_wrap.instance)
                    try:
                        result = self.run(instance=instance_wrap.instance)
                    except:
                        print("validation failed")
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
        self.instances = []  # plugin_instances
        super().__init__()

    def run(self):
        for plugin_class in self.registered_plugins:
            print("running", plugin_class)
            plugin_instance = plugin_class(parent=self)
            self.instances.append(plugin_instance)
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


class CollectHelloWorld(Collector):
    def run(self):
        print('CollectHelloWorld run')
        return ["Hello World"]


class CollectHelloWorldList(Collector):
    def run(self):
        print('CollectHelloWorldList run')
        return ["Hello", "World"]


class ValidateHelloWorld(Validator):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.state = None
        # state can be run, error, not_yet_ran, running
        self.state = 'not_yet_ran'

    def run(self, instance):
        self.state = 'running'
        print('ValidateHelloWorld run')
        assert instance == "Hello World"
        self.state = 'success'


session = Session()
session.registered_plugins.append(CollectHelloWorld)
session.registered_plugins.append(CollectHelloWorldList)
session.registered_plugins.append(ValidateHelloWorld)
session.run()

# print validation results instances
for plugin in session.instances:
    print(plugin)
    print(plugin.instances)
    for inst in plugin.instances:
        print('STATE', inst, inst.parent, inst.parent.state)  # TODO get validation state, atm we get parent(collect) state

# CollectHelloWorld run
# CollectHelloWorldList run
# <__main__.CollectHelloWorld object at 0x0000018B2909D790>
# 1 [InstanceWrapper(Hello World)]
# <__main__.CollectHelloWorldList object at 0x0000018B2909A550>
# 2 [InstanceWrapper(Hello), InstanceWrapper(World)]



# register collector
# register validator

# run registered plugins in order



# class collect_meshes_blender():
#     def run(self):
#         """Collect meshes from Blender"""
#         meshes = []
#         for obj in bpy.context.selected_objects:
#             if obj.type == 'MESH':
#                 meshes.append(obj)
#         return meshes
#
#
# class validate_meshes_vertcount():
#     def run(self):
#         """Validate meshes have the correct number of vertices"""
#         for mesh in meshes:
#             if len(mesh.data.vertices) < 3:
#                 return False
#         return True


# class validate_meshes_vertcount_dependant():
#     def run(self):
#         """Validate meshes have the correct number of vertices"""
#         for mesh in meshes:
#             if len(mesh.data.vertices) < 3:
#                 return False
#         return True