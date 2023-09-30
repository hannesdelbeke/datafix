from unittest import TestCase
from pac2.node import Node, ProcessNode, NodeState
import pac2.node


class TestNode(TestCase):
    def test_node_name(self):
        a = Node(name="test")
        assert a.name == "test"

    def test_output_nodes(self):
        # test connecting a node to another node's attribute
        a = Node(name="a")
        b = Node(name="b", data="hello")
        a.name = b  # todo nodemodel
        assert a.name == "hello"

    def test_cached_result(self):
        # test that a node's output is cached
        node = ProcessNode(callable=lambda x: x + 1)
        result = node(3)  # process node
        assert result == 4
        assert node.data == 4

    # def test_config(self):
    #     a = Node(name="a")
    #     c = Node(name="c")
    #     b = Node(name="b")
    #     a.parent = b
    #     b.parent = c
    #     data = a.config()  # serialise
    #     a2 = Node.graph_from_config(data)  # deserialise
    #     assert a2.parent.id == b.id

    def test_output_links(self):
        a = Node(name="a")
        b = Node(name="b")
        a.connect(b)  # todo replace
        assert len(a.output_links) == 1, f"should have 1 output link, but has {len(a.output_links)}, {a.output_links}"

    def test_output_links(self):
        print("test_output_links---")
        a = Node(name="a", data="hello")

        has_run = []

        def print_string(string):
            print("print string", string)
            has_run.append(string)

        print("make node model")
        node_model = pac2.node.node_model_class_from_callable(print_string)
        print("make node class")
        node_class = ProcessNode.class_from_callable_class(node_model)
        print("make node")
        b = node_class(name="b")
        print("connect")
        a.connect(b, attr_in="string")  # todo replace
        print("--- run b ---")
        b()
        print("--- finish run b ---")
        assert has_run == ["hello"], f"should have run once, but has run {has_run}"

    # def test_runtime_connection(self):
    #     def temp_method():
    #         return "hello"
    #
    #     a = ProcessNode(name="a", raise_exception=True)
    #     b = ProcessNode(name="b", callable=temp_method, raise_exception=True)
    #
    #     def get_b_output():
    #         return b()
    #
    #     a.callable = get_b_output
    #     result = a()
    #     assert result == "hello"
    #     assert a.runtime_connections == {b}, f"should be [Node(b)] but is {a.runtime_connections}"
    #     assert b in a.connected_nodes, f"connected_nodes should contain Node(b), but is {a.connected_nodes}"
    #
    #     # test recursion level 2
    #     def temp_method2():
    #         return "hello2"
    #
    #     c = ProcessNode(name="c", callable=temp_method2, raise_exception=True)
    #
    #     def get_c_output():
    #         return c()
    #
    #     b.callable = get_c_output
    #     result = a()
    #     assert result == "hello2"
    #     assert a.runtime_connections == {b}, f"should be [Node(b)] but is {a.runtime_connections}"
    #     assert b.runtime_connections == {a, c}, f"should be [Node(a), Node(c)] but is {b.runtime_connections}"

    def test_collect_nodes_from_module(self):
        from tests import test_modules

        nodes = [x for x in Node.nodes_from_module(test_modules)]
        assert [x.name for x in nodes] == [
            "NodeA1",
            "NodeA2",
            "NodeB1",
            "NodeB2",
            "NodeC1",
            "NodeC2",
            "NodeD1",
            "NodeD2",
        ]

    def test_linear_pipeline(self):
        """
        connect nodes in a linear pipeline.
        Running the last node should run all nodes in the pipeline
        """
        temp = []
        a = ProcessNode(name="A", callable=lambda: temp.append("a"))
        b = ProcessNode(name="B", callable=lambda: temp.append("b"))
        c = ProcessNode(name="C", callable=lambda: temp.append("c"))
        d = ProcessNode(callable=lambda: temp.append("d"))

        a.connect(b)
        b.connect(c)

        c()

        assert a.state == NodeState.SUCCEED
        assert b.state == NodeState.SUCCEED
        assert c.state == NodeState.SUCCEED
        assert d.state == NodeState.INIT  # d is not hooked up to the pipeline
        assert temp == ["a", "b", "c"]

    def test_linear_pipeline2(self):
        """
        connect nodes in a linear pipeline.
        Running the last node should run all nodes in the pipeline
        """
        temp = []
        a = ProcessNode(name="A", callable=lambda: temp.append("a"))
        b = ProcessNode(name="B", callable=lambda: temp.append("b"))
        c = ProcessNode(name="C", callable=lambda: temp.append("c"))

        # A - B - C
        a.connect(b)  # A in B
        b.connect(c)  # A in B out C
        a.connect(c)  # disconnect b
        # A in C, connects to call slot, overrides b
        # get node c, get attr in (call slot),

        c()

        assert a.state == NodeState.SUCCEED
        assert b.state == NodeState.INIT
        assert c.state == NodeState.SUCCEED
        assert temp == ["a", "c"]
        assert b.output_nodes == [], f"b.output_nodes should be empty, but is {b.output_nodes}"

    def test_connection(self):
        """test that we dont store duplicate connections"""
        a = ProcessNode(name="A", callable=lambda: 1)
        b = ProcessNode(name="B", callable=lambda: 1)
        a.connect(b)
        a.connect(b)
        a.connect(b)
        b()
        assert a.state == NodeState.SUCCEED
        assert b.state == NodeState.SUCCEED
        assert a.output_nodes == [b], f"should be [Node(b)] but is {a.output_nodes}"
        assert len(a._output_links) == 1
        assert len(b._input_links) == 1
