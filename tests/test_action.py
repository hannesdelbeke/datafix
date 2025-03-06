import logging

from datafix.core import Session, Validator, Action, Collector, Node, NodeState


# actions are callables that can be run on a node.
# they also can have settings
# e.g. browse to path
# def browse_to_path(node, path):
#     ...
# action also needs a name, mainly for UI purposes.

class ActionPrintHello(Action):
    def action(self):
        return 'Hello'


class ActionFail(Action):
    def action(self):
        raise Exception('Fail')


class ActionPrintChildNodes(Action):
    def action(self):
        print(f"action: {self.parent.children}")


class CollectHelloWorld(Collector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def collect(self):
        return ["Hello World"]

class CollectWithAction(Collector):
    # action_classes = [ActionPrintChildNodes]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions = [ActionPrintChildNodes(parent=self)]

    def collect(self):
        return ["Hello World"]


class CollectHelloWorldList(Collector):
    def collect(self):
        return ["Hello", "World"]


class ValidateHelloWorld(Validator):
    def validate(self, data):
        assert data == "Hello World"


def test_action_print_child_nodes():
    session = Session()
    collector = CollectHelloWorld(parent=session)
    collector.actions.append(ActionPrintChildNodes(parent=collector))
    session.run()

    collector.actions[0].run()


def test_externally_register_action():
    """test that registering actions doesn't affect other nodes of same class"""
    session = Session()
    collector1 = CollectHelloWorld(parent=session)
    collector2 = CollectHelloWorld(parent=session)

    action = ActionPrintHello(parent=collector1)
    collector1.actions.append(action)

    assert collector1.actions[0] == action
    assert collector2.actions == []

    session.run()
    logging.error(collector1.actions)
    logging.error(collector2.actions)

    assert collector1.actions[0] == action
    assert collector2.actions == []


def test_action_fail():
    action = ActionFail()
    action.run()
    assert action.state == NodeState.FAIL

def test_action_fail2():
    session = Session()
    collector = CollectHelloWorld(parent=session)
    action = ActionFail(parent=collector)
    collector.actions.append(action)
    session.run()
    # if an action fails, the collector should maintain it's success state
    assert collector.state == NodeState.SUCCEED


# def _test_action_results():
#     # create a node with 2 actions, and store the action results for that node
#     # check if action results are stored, and is accessible from node
#
#     node = Node()
#     node.actions = [ActionPrintHello(), ActionFail()]
#     # run both actions
#     for action in node.actions:
#         action.run()
#
#     action_1, action_2 = node.actions
#     assert action_1._state == NodeState.SUCCEED
#     assert action_2._state == NodeState.FAIL
#
#     for action in node.actions:
#         action.run()
#     assert action_1._state == NodeState.SUCCEED
#     assert action_2._state == NodeState.FAIL
#     # TODO better handle state and result. unify state and result.?
#
#     # if we have a mixed result / success.
#     # action should return the lowest result
#     # CRITICAL 50
#     # ERROR 40
#     # WARNING 30
#     # INFO 20
#     # DEBUG 10
#     # NOTSET 0
#
#     # SUCCESS
#     # FAIL
#     # SKIPPED?
#     # NOT RUN
#     # FAIL BUT CONTINUE (WARNING)
