"""Tests for the node_state_setter context manager."""

from datafix.core.node import Node, NodeState


def test_node_state_setter_success():
    """Test that node_state_setter correctly sets state to SUCCEED on success."""
    node = Node()
    assert node.state == NodeState.INIT
    with node.node_state_setter():
        assert node.state == NodeState.RUNNING
        pass
    assert node.state == NodeState.SUCCEED


def test_node_state_setter_failure():
    """Test that node_state_setter correctly sets state to FAIL on exception."""
    node = Node()
    assert node.state == NodeState.INIT
    with node.node_state_setter():
        assert node.state == NodeState.RUNNING
        raise ValueError("Test error")
    assert node.state == NodeState.FAIL


def test_node_state_setter_warning_mode():
    """Test that node_state_setter respects warning mode."""
    node = Node()
    node.warning = True
    with node.node_state_setter():
        raise ValueError("Test error")
    assert node.state == NodeState.WARNING


# def test_node_state_setter_continue_on_fail():
#     """Test that node_state_setter respects continue_on_fail setting."""
#     node = Node()
#     node.continue_on_fail = True

#     # Should not raise exception
#     with node.node_state_setter():
#         raise ValueError("Test error")

#     assert node.state == NodeState.FAIL


# def test_node_state_setter_no_continue_on_fail():
#     """Test that node_state_setter raises exception when continue_on_fail=False."""
#     node = Node()
#     node.continue_on_fail = False

#     # Should raise exception
#     with pytest.raises(ValueError):
#         with node.node_state_setter():
#             raise ValueError("Test error")

#     assert node.state == NodeState.FAIL
