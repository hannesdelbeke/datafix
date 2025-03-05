import logging
from enum import Enum
from typing import List
from contextlib import contextmanager


def color_text(text, state):
    """format text to support color (green or red) in the console based on state"""
    if state == NodeState.SUCCEED:
        text = f'\033[32m{text}\033[0m'  # green
    elif state == NodeState.FAIL:
        text = f'\033[31m{text}\033[0m'  # red
    return text


# inspiration https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-map-state.html
# success could be 0, everything else is a failure/warning ...
class NodeState(Enum):
    INIT = "initialized"  # not run
    SUCCEED = "succeed"  # run and success, match AWS
    FAIL = "fail"  # run and exception, match AWS
    RUNNING = "running"  # run and running / in progress
    WARNING = "warning"  # warning
    # PAUSED = "paused"
    # STOPPED = "stopped"
    # SKIPPED = "skipped"
    # DISABLED = "disabled"
    # PASS
    # WAIT
    # CHOICE


class Node:
    continue_on_fail = True  # if self or any children fail, continue running
    warning = False  # set state to WARNING if this node FAILS

    def __init__(self, parent=None, name=None):
        # self.action_class = None
        self.actions = []

        # when you run a node, it runs all child nodes.
        # collectors create new DataNodes and make them children
        # validators run, with DataNodes as input
        #     results saved
        # actions run on ...

        self.parent = parent  # node that created this node
        if parent:
            parent.children.append(self)
        self.children: "List[Node]" = []  # nodes created by this node
        # TODO instead of storing result in 1 node, and then querying this node from the other node for the result.
        #  we can store the result in the link/connection between nodes

        self._state = NodeState.INIT
        self.name = name or self.__class__.__name__

    @property
    def state(self):
        # a session fails if any nodes in it fail
        # a collector fails if it fails to collect, it doesn't care about it's children
        # a validator fails if any of the datanodes it runs on fails
        # an instance node fails if any validations on it fail
        if self._state == NodeState.FAIL and self.warning:
            return NodeState.WARNING
        return self._state
        #
        # if self.children:
        #     # if this node has children, it's a collector, validator, or session
        #     # we check the state of the children
        #     for child in self.children:
        #         if child.state == NodeState.FAIL:
        #             return NodeState.FAIL
        #     return NodeState.SUCCEED
        # else:
        #     # if this node has no children, it's an instance node
        #     # we check the state of the instance node
        #     return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def session(self):
        """get the session this node belongs to (the top node)"""
        if self.parent:
            return self.parent.session
        else:
            return self

    def logic(self):
        """inherit and overwrite this"""
        raise NotImplementedError

    def run(self, *args, **kwargs):
        # if we run the session, it runs all registered nodes under it.
        # e.g. collector first, then validate on the collected data
        # to ensure you first run collector and then validator, register in order.

        # logging.info(f'running {self.__class__.__name__}')
        with node_state_setter(self):
            result = self.logic(*args, **kwargs)

    def report(self) -> str:
        """"create a report of this node and it's children"""
        txt = f'{self.pp_state}\n'

        import textwrap
        for child in self.children:
            txt_child = child.report()
            txt += textwrap.indent(txt_child, '  ')
        return txt

    @property
    def pp_state(self) -> str:
        """
        return a pretty print string for this Node & it's state
        e.g. 'DataNode(Hello): succeed'
        """
        state = color_text(state=self.state, text=self.state.value)
        return f'{self}: {state}'

    def __repr__(self):
        return f'{self.__class__.__name__}'

    def log_error(self, text):
        if self.warning:
            logging.warning(text)
        else:
            logging.error(text)


class StateSetter:
    def __enter__(self, node):
        # Setup logic (executed before the "with" block)
        node._state = NodeState.RUNNING
        return self  # Optionally return something to use in the block

    def __exit__(self, exc_type, exc_value, traceback):
        # Teardown logic (executed after the "with" block)
        print("Exiting the context")
        if exc_type:
            print(f"An exception occurred: {exc_value}")
        return True  # Suppress exceptions if necessary (optional)


@contextmanager
def node_state_setter(node: Node):
    """a context manager to set the state of a node, and handle exceptions"""
    try:
        # Set the node state to RUNNING at the start
        node._state = NodeState.RUNNING

        yield  # Logic inside the 'with' block executes here

        # check state is not fail or warning, in case something set it to fail
        if node.state == NodeState.RUNNING:
            # Set the node state to SUCCEED if no exception occurs
            node._state = NodeState.SUCCEED
    except Exception as e:
        # On exception, set the node state to FAIL and log the error
        node._state = NodeState.FAIL
        node.log_error(f"'{node.__class__.__name__}' failed running: '{e}'")
        if not node.continue_on_fail:
            raise e  # Rethrow the exception if continue_on_fail is False
