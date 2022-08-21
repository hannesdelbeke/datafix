from pac.logic import *


def collect_hello_world(*args, **kwargs):
    return ["Hello World"]

def collect_hello_world_list(*args, **kwargs):
    return ["Hello", "World"]


class ActionCollectHelloWorld(ActionCollect):
    run = collect_hello_world


class ActionCollectHelloWorldList(ActionCollect):
    run = collect_hello_world_list


class CollectHelloWorld(Collector):
    action_class = ActionCollectHelloWorld

class CollectHelloWorldList(Collector):
    action_class = ActionCollectHelloWorldList



# class CollectHelloWorld(Collector):
#     def run(self):
#         return ["Hello World"]
#
#
# class CollectHelloWorldList(Collector):
#     def run(self):
#         return ["Hello", "World"]
#
#
# class ValidateHelloWorld(Validator):
#     def __init__(self, parent):
#         super().__init__(parent=parent)
#         self.state = None
#         # state can be run, error, not_yet_ran, running
#         self.state = 'not_yet_ran'
#
#     def run(self, instance):
#         assert instance == "Hello World"


def main():
    session = Session()
    # session.registered_plugins.append(CollectHelloWorld)
    # session.registered_plugins.append(CollectHelloWorldList)
    # session.registered_plugins.append(ValidateHelloWorld)
    session.registered_plugins.append(CollectHelloWorld)
    session.registered_plugins.append(CollectHelloWorldList)
    session.run()

    print()
    # print validation results instances
    for plugin in session.plugin_instances:
        print(plugin)
        print(plugin.children)
        for inst in plugin.children:
            print('STATE', inst, inst.parent, inst.parent.state)  # TODO get validation state, atm we get parent(collect) state

    # rerun collector 1
    session.children[0]._run()
    session.children[0]._run()
    session.children[0]._run()

    print()
    import pprint
    pp = pprint.pp
    pp(session.tree())

if __name__ == '__main__':
    main()