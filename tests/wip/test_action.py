from datafix import *
from datafix.core import Session, Validator, Action, Collector, Node, NodeState


class ActionPrintHello(Action):
    def collect(self):
        return 'Hello'


class ActionFail(Action):
    def logic(self):
        raise Exception('Fail')


class CollectHelloWorld(Collector):
    def __init__(self, parent):
        super().__init__()
        self.actions = [ActionPrintHello(parent=self)]

    def collect(self):
        return ["Hello World"]


class CollectHelloWorldList(Collector):
    def collect(self):
        return ["Hello", "World"]


class ValidateHelloWorld(Validator):
    def validate(self, data):
        assert data == "Hello World"


def test_simple_action():
    session = Session()
    session.add(CollectHelloWorld)
    session.add(CollectHelloWorldList)
    session.add(ValidateHelloWorld)
    session.run()

    collector_instance = session.children[0]
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
    assert action_1._state == NodeState.SUCCEED
    assert action_2._state == NodeState.FAIL

    for action in node.actions:
        action.run()
    assert action_1._state == NodeState.SUCCEED
    assert action_2._state == NodeState.FAIL
    # TODO better handle state and result. unify state and result.?

    # if we have a mixed result / success.
    # action should return the lowest result
    # CRITICAL 50
    # ERROR 40
    # WARNING 30
    # INFO 20
    # DEBUG 10
    # NOTSET 0

    # SUCCESS
    # FAIL
    # SKIPPED?
    # NOT RUN
    # FAIL BUT CONTINUE (WARNING)
