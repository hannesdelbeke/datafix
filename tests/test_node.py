from datafix.core.node import Node, NodeState


def test_set_state_from_children():
    node: Node = Node()
    node.children = [Node(), Node()]
    node.children[0].state = NodeState.SUCCEED
    node.children[1].state = NodeState.FAIL
    state = node.set_state_from_children()

    assert state == NodeState.FAIL

    node.children[0].state = NodeState.SUCCEED
    node.children[1].state = NodeState.INIT
    state = node.set_state_from_children()

    assert state == NodeState.SUCCEED
