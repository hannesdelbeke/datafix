from pac.logic import *


class CollectHelloWorld(Collector):
    def _run(self):
        return ["Hello World"]


class CollectHelloWorldList(Collector):
    def _run(self):
        return ["Hello", "World"]


class ValidateHelloWorld(Validator):
    def validate_instance(self, instance):
        assert instance == "Hello World"


def test_simple_session2():
    session = Session()
    session.registered_plugins.append(CollectHelloWorld)
    session.registered_plugins.append(CollectHelloWorldList)
    session.registered_plugins.append(ValidateHelloWorld)
    session.run()

    # wrap_a = session.plugin_instances[0].instance_wrappers[0]
