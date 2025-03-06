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

def test_warning():
    node: Node = Node()
    node.state = NodeState.FAIL
    node.warning = True
    assert node.state == NodeState.WARNING

def test_warning_2_nodes():
    # since we use a class variable ensure it doesn't affect all classes
    node1: Node = Node()
    node2: Node = Node()
    node1.state = NodeState.FAIL
    node2.state = NodeState.FAIL
    node1.warning = True
    assert node2.warning == False
    assert node2.state == NodeState.FAIL