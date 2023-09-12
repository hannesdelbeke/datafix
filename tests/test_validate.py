from unittest import TestCase
from pac2.node import Node, ValidatorNode


class TestValidate(TestCase):  # todo name
    def test_validation(self):
        string_node = Node(data="hello")
        int_node = Node(data=1)
        validator_node = ValidatorNode(input_nodes=[string_node, int_node])
        # create mesh and texture instance
        # create mesh validator
        # test if validator only runs on mesh instances
