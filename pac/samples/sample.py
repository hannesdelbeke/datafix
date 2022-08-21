from pac.port import *


class CollectHelloWorld(Collector):
    def _run(self):
        return ["Hello World"]


class CollectHelloWorldList(Collector):
    def _run(self):
        return ["Hello", "World"]


class ValidateHelloWorld(Validator):
    def validate_instance(self, instance):
        assert instance == "Hello World"

    # def _run(self):
    #     assert instance == "Hello World"


def main():
    session = Session()
    session.registered_plugins.append(CollectHelloWorld)
    session.registered_plugins.append(CollectHelloWorldList)
    session.registered_plugins.append(ValidateHelloWorld)
    session.run()

    print()
    # # print validation results instances
    # for plugin in session.plugin_instances:
    #     print(plugin)
    #     print(plugin.children)
    #     for inst in plugin.children:
    #         print('STATE', inst, inst.parent, inst.parent.state)  # TODO get validation state, atm we get parent(collect) state

    session.pp_tree()
if __name__ == '__main__':
    main()