from pac.logic import *


class ActionPrintHello(Action):
    def _run(self):
        return 'Hello'


class ActionFail(Action):
    def _run(self):
        raise Exception('Fail')


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


def test_simple_action():
    session = Session()
    session.registered_plugins.append(CollectHelloWorld)
    session.registered_plugins.append(CollectHelloWorldList)
    session.registered_plugins.append(ValidateHelloWorld)
    session.run()

    collector_instance = session.plugin_instances[0]
    assert 'Hello' == collector_instance.actions[0].run()


def test_action_results():
    # create a node with 2 actions, and store the action results for that node
    # check if action results are stored, and is accessible from node

    node = Node()
    node.actions = [ActionPrintHello(parent=node), ActionFail(parent=node)]
    # run both actions
    for action in node.actions:
        action.run()

    action_1, action_2 = node.actions
    assert action_1.state == NodeState.SUCCEED
    assert action_2.state == NodeState.FAIL

    for action in node.actions:
        action.run()
    assert action_1.state == NodeState.SUCCEED
    assert action_2.state == NodeState.FAIL
