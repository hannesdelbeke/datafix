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
        result = node(3)  # process node
        assert result == 4
        assert node.data == 4

    def test_output_links(self):
        a = Node(name="a")
        b = Node(name="b", data="hello")
        a.parent = b
        assert len(b.output_links) == 1, f"should have 1 output link, but has {len(b.output_links)}, {b.output_links}"

    def test_runtime_connection(self):
        def temp_method():
            return "hello"

        a = ProcessNode(name="a", raise_exception=True)
        b = ProcessNode(name="b", callable=temp_method, raise_exception=True)

        def get_b_output():
            return b()

        a.callable = get_b_output
        result = a()
        assert result == "hello"
        assert a.runtime_connections == {b}, f"should be [Node(b)] but is {a.runtime_connections}"
        assert b in a.connected_nodes, f"connected_nodes should contain Node(b), but is {a.connected_nodes}"

        # test recursion level 2
        def temp_method2():
            return "hello2"

        c = ProcessNode(name="c", callable=temp_method2, raise_exception=True)

        def get_c_output():
            return c()

        b.callable = get_c_output
        result = a()
        assert result == "hello2"
        assert a.runtime_connections == {b}, f"should be [Node(b)] but is {a.runtime_connections}"
        assert b.runtime_connections == {a, c}, f"should be [Node(a), Node(c)] but is {b.runtime_connections}"

    def test_collect_nodes_from_module(self):
        from tests import test_modules

        nodes = [x for x in Node.create_nodes_from_module(test_modules)]
        print(nodes)
