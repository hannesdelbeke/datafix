import logging
from enum import Enum
from typing import List
from contextlib import contextmanager


DEBUG_MODE = False


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
    """
    warning: if True, warn instead of fail. A warning implies accepted failure.
    continue_on_fail: if True, continue running even if this node fails
    """
    continue_on_fail = True  # if self or any children fail, continue running
    warning = False  # set state to WARNING if this node FAILS
    # action_classes = []

    # Action-classes, that will be added to self.actions on instance
    # the main reason we instance on init, is so each node has it's own action
    # so we can track fail success of actions per node
    # E.G. a select mesh action, defined by a mesh collector, is auto added to all mesh-Nodes
    child_actions = None # should be empty list but mutate bug
    name = None

    def __init__(self, parent:"Node|None"=None, name=None):
        self.actions = []  # instanced action nodes, that can be run on this node
        self.children: "List[Node]" = []  # nodes created by this node
        self.parent = parent  # node that created this node

        self.child_actions = self.child_actions or []

        if name:
            self.name = str(name)
        else:
            self.name = self.__class__.__name__

        if parent:
            if parent is self:
                raise ValueError(f"Node '{self}' cannot be its own parent")

            # add any node created by another node, to the parent's children
            parent.children.append(self)

            # add any child actions defined in the parent, to this node
            for action in parent.child_actions:
                # print(parent.child_actions)
                self.actions.append(action(parent=self))

        self._state = NodeState.INIT

        # self.actions = [action(parent=self) for action in self.action_classes]
        # # auto parent doesn't work, because the parent is not yet created. so manually populate children
        # self.children = copy(self.actions)


    @property
    def state(self):
        if self._state == NodeState.FAIL and self.warning:
            return NodeState.WARNING
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    def set_state_from_children(self):
        # todo make part of node class
        """fail if a child fails, also fail if a parent fails"""
        # a validator fails if any of the DataNodes it runs on fails
        # or if the validator itself fails
        if self.state == NodeState.FAIL:
            self.state = NodeState.FAIL

        child_states = [child_node.state for child_node in self.children]

        if NodeState.FAIL in child_states:
            # a child failed
            self.state = NodeState.FAIL
        elif NodeState.WARNING in child_states:
            # a child has a warning
            self.state = NodeState.WARNING
        # elif all([state == NodeState.SUCCEED for state in child_states]):
        else:
            # all children succeeded
            self.state = NodeState.SUCCEED
        # else:
        # some children are still running, or didn't run, or other ...
        # this shouldn't happen unless maybe if nodes are still running
        # this can also trigger if you used reload AFAIK
        # raise NotImplementedError(f"Node {self} has children in state {child_states}")

        return self.state

    @property
    def session(self):
        """get the session this node belongs to (the top node)"""
        if self.parent:
            return self.parent.session
        else:
            return self

    def run(self, *args, **kwargs):
        raise NotImplementedError

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

    def __getitem__(self, item: "str|Node"):
        """ get a child-node by name, returns first node if multiple
        e.g. session["collector_name"] """
        for node in self.children:
            if node.name == item:
                return node
        return None

    def get(self, item: "str|Node", default=None):
        """ get a child-node by name, returns first node if multiple
        e.g. session.get("collector_name") """
        return self[item] or default

    # def __setitem__(self, key, value):
    #     """ set a child-node by name, doesn't overwrite existing nodes but creates multiple of same name
    #     shouldn't use this tbh, use CollectorNode(parent=self, name="collector_name") instead
    #     e.g. session["collector_name"] = collector_node """
    #     value.name = key
    #     value.parent = self

    # def __delitem__(self, key: "str|Node"):
    #     """ remove a child-node by name or node-instance
    #     e.g. del session["collector_name"] """
    #     if isinstance(key, str):
    #         for node in self.children:
    #             if node.name == key:
    #                 self.children.remove(node)
    #                 return
    #     else:
    #         self.children

    def delete(self):
        """delete self and all child-nodes, remove self from parent"""
        self.delete_children()
        if self.parent:
            self.parent.children.remove(self)

    def delete_children(self, type=None):
        """delete all child-nodes, keep self"""
        for child in list(self.children):  # list so we can delete while iterating
            child.delete()

    # def __iter__(self):
    #     return iter(self.children)

    # def __len__(self):
    #     return len(self.children)

    # def __contains__(self, item: "str|Node"):
    #    confusing if len returns child length,
    #    but the contains method recursively checks children (bigger than len)
    #     """ recursively check if a node is a child. Takes either a node-instance or node-name
    #     e.g. "collector_name" in session """
    #     if isinstance(item, str):
    #         for child in self.children:
    #             if item == child.name or item in child:
    #                 return True
    #     else:
    #         for child in self.children:
    #             if item == child or item in child:
    #                 return True


@contextmanager
def node_state_setter(node: Node):
    """a context manager to set the state of a node, and handle exceptions"""
    try:
        # Set the node state to RUNNING at the start
        node._state = NodeState.RUNNING
        yield  # Logic inside the 'with' block executes here
        # check state is not fail or warning, in case something set it to fail while it ran
        if node.state == NodeState.RUNNING:
            node._state = NodeState.SUCCEED
    except Exception as e:
        # On exception, set the node state to FAIL and log the error
        node._state = NodeState.FAIL
        node.log_error(f"'{node.__class__.__name__}' failed running: '{e}'")
        if DEBUG_MODE or not node.continue_on_fail:
            raise e  # Rethrow the exception if continue_on_fail is False

