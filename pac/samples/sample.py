from pac.port import *


def collect_hello_world():
    return ["Hello World"]

def collect_hello_world_list():
    return ["Hello", "World"]


class ActionCollectHelloWorld(Action):
    run = collect_hello_world


class ActionCollectHelloWorldList(Action):
    run = collect_hello_world_list


class CollectHelloWorld(Collector):
    def run(self):
        return ["Hello World"]



class CollectHelloWorld(Collector):
    def run(self):
        return ["Hello World"]


class CollectHelloWorldList(Collector):
    def run(self):
        return ["Hello", "World"]


class ValidateHelloWorld(Validator):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.state = None
        # state can be run, error, not_yet_ran, running
        self.state = 'not_yet_ran'

    def run(self, instance):
        assert instance == "Hello World"


def main():
    session = Session()
    session.registered_plugins.append(CollectHelloWorld)
    session.registered_plugins.append(CollectHelloWorldList)
    session.registered_plugins.append(ValidateHelloWorld)
    session.run()

    print()
    # print validation results instances
    for plugin in session.plugin_instances:
        print(plugin)
        print(plugin.children)
        for inst in plugin.children:
            print('STATE', inst, inst.parent, inst.parent.state)  # TODO get validation state, atm we get parent(collect) state

if __name__ == '__main__':
    main()