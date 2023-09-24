from unittest import TestCase
from pac2.node import Node, ProcessNode, NodeState


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

        nodes = [x for x in Node.nodes_from_module(test_modules)]
        assert [x.name for x in nodes] == ["NodeA1", "NodeA2", "NodeB1", "NodeB2", "NodeC1", "NodeC2", "NodeD1", "NodeD2"]

    def test_linear_pipeline(self):
        """
        connect nodes in a linear pipeline.
        Running the last node should run all nodes in the pipeline
        """
        temp = []
        a = ProcessNode(name="A", callable=lambda : temp.append("a"))
        b = ProcessNode(name="B", callable=lambda : temp.append("b"))
        c = ProcessNode(name="C", callable=lambda : temp.append("c"))
        d = ProcessNode(callable=lambda : temp.append("d"))

        a.OUT = b  # same as b.IN = a, except IN can have multiple inputs
        b.OUT = c
        # todo how to not confuse this with b.my_input_attr = c
        #  which means b.my_input_attr = c.data (__call__)

        c()

        assert a.state == NodeState.SUCCEED
        assert b.state == NodeState.SUCCEED
        assert c.state == NodeState.SUCCEED
        assert d.state == NodeState.INIT  # d is not hooked up to the pipeline
        assert temp == ["a", "b", "c"]

    def test_linear_pipeline(self):
        """
        connect nodes in a linear pipeline.
        Running the last node should run all nodes in the pipeline
        """
        temp = []
        a = ProcessNode(name="A", callable=lambda: temp.append("a"))
        b = ProcessNode(name="B", callable=lambda: temp.append("b"))
        c = ProcessNode(name="C", callable=lambda: temp.append("c"))

        a.OUT = b  # same as b.IN = a, except IN can have multiple inputs
        c.IN = b
        # todo how to not confuse this with b.my_input_attr = c
        #  which means b.my_input_attr = c.data (__call__)

        c()

        assert a.state == NodeState.SUCCEED
        assert b.state == NodeState.SUCCEED
        assert c.state == NodeState.SUCCEED
        assert temp == ["a", "b", "c"]
        # assert b.OUT == c # todo

    def test_linear_pipeline_greater_than(self):
        """
        connect nodes in a linear pipeline.
        Running the last node should run all nodes in the pipeline
        """
        temp = []
        a = ProcessNode(name="A", callable=lambda: temp.append("a"))
        b = ProcessNode(name="B", callable=lambda: temp.append("b"))
        c = ProcessNode(name="C", callable=lambda: temp.append("c"))

        a > b > c  # todo how not to confuse this with 5 > a.my_int (returning a bool)

        c()

        assert a.state == NodeState.SUCCEED
        assert b.state == NodeState.SUCCEED
        assert c.state == NodeState.SUCCEED
        assert temp == ["a", "b", "c"]

        # # test changing pipeline -------
        # temp = []
        #
        # b.IN = None
        # b.OUT = a
        # a.OUT = c
        # c()
        # assert temp == ["c", "a"]
        # # ---------------------------


        # # try:
        # b.OUT = a  # attempt to make a loop, should fail
        # #     raise Exception("should not be able to make a loop")
        # # except Exception as e: # todo what exception should this be?
        # #     pass

    # def test_non_linear_pipeline(self):
    #     """
    #     connect nodes in a non-linear pipeline.
    #     Running the last node should run all nodes in the pipeline
    #     """
    #     temp = []
    #     a = ProcessNode(callable=lambda : temp.append("a"))
    #     b = ProcessNode(callable=lambda : temp.append("b"))
    #     c = ProcessNode(callable=lambda : temp.append("c"))
    #     d = ProcessNode(callable=lambda : temp.append("d"))
    #
    #     a > c
    #     b > c > d
    #
    #     print("START D==============")
    #     d()
    #
    #     assert a.state == NodeState.SUCCEED
    #     assert b.state == NodeState.SUCCEED
    #     assert c.state == NodeState.SUCCEED
    #     assert d.state == NodeState.SUCCEED
    #     assert temp == ["a", "b", "c", "d"]