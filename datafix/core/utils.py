from datafix.core import Node, NodeState



def set_state_from_children(node:Node):
    """fail if a child fails, also fail if a parent fails"""
    # a validator fails if any of the DataNodes it runs on fails
    # or if the validator itself fails
    if node.state == NodeState.FAIL:
        node.state = NodeState.FAIL

    child_states = [child_node.state for child_node in node.children]

    if NodeState.FAIL in child_states:
        # a child failed
        node.state = NodeState.FAIL
    elif NodeState.WARNING in child_states:
        # a child has a warning
        node.state = NodeState.WARNING
    elif all([state == NodeState.SUCCEED for state in child_states]):
        # all children succeeded
        node.state = NodeState.SUCCEED
    else:
        # some children are still running, or didn't run, or other ...
        # this shouldn't happen unless maybe if nodes are still running
        raise NotImplementedError