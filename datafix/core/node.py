import logging
from enum import Enum
from typing import List


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
        self.children: "List[Node]" = []  # nodes created by this node
        self.connections = []  # related nodes
        # TODO instead of storing result in 1 node, and then querying this node from the other node for the result.
        #  we can store the result in the link/connection between nodes

        self._state = NodeState.INIT
        # self.name = name

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

    def _run(self, *args, **kwargs):
        """inbetween function to handle state"""
        return self.logic()

    def logic(self):
        """inherit and overwrite this"""
        raise NotImplementedError

    def run(self, *args, **kwargs):
        # if we run the session, it runs all registered nodes under it.
        # e.g. collector first, then validate on the collected data
        # to ensure you first run collector and then validator, register in order.
        logging.info(f'running {self.__class__.__name__}')

        # result = None
        try:
            self._state = NodeState.RUNNING
            result = self._run(*args, **kwargs)
            self._state = NodeState.SUCCEED
        except Exception as e:
            self._state = NodeState.FAIL
            self.log_error(f"'{self.__class__.__name__}' failed running:'{e}'" )
            if not self.continue_on_fail:
                raise e

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
