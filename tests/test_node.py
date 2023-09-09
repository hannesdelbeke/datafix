from unittest import TestCase
from pac2.node import Node, NodeState


class TestNode(TestCase):
    def test_node_name(self):
        a = Node(name="test")
        assert a.name == "test"

    def test_output_nodes(self):
        # test connecting a node to another node's attribute
        a = Node(name="a")
        b = Node(name="b", data="hello")
        a.name = b
        assert a.name == "hello"
