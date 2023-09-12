from unittest import TestCase
from pac2.node import Node, ProcessNode


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

    def test_cached_result(self):
        # test that a node's output is cached
        node = ProcessNode(callable=lambda x: x + 1)
        result = node.output(3)  # process node
        assert result == 4
        assert node.data == 4

    def test_parent(self):
        a = Node(name="a")
        b = Node(name="b")
        a.parent = b

        assert a.parent == b

    # def test_config(self):
    #     # todo serialise deserialise
    #     a = Node(name="a")
    #     b = Node(name="b")
    #     a.parent = b
    #
    #     print("PARENT", a.parent)
    #     data = a.to_config()
    #     import pprint
    #     pprint.pprint(data)
    #     # save out this graph
    #     # take a random node, and ask for the connected nodes to get graph
