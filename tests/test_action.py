from pac.logic import *


class ActionPrintHello(Action):
    def _run(self):
        return 'Hello'

class CollectHelloWorld(Collector):
    def __init__(self, parent):
        super().__init__()
        self.actions = [ActionPrintHello(parent=self)]

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

    collector_instance = session.plugin_instances[0]
    assert 'Hello' == collector_instance.actions[0].run()
