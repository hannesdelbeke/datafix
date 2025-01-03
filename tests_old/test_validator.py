from pac.logic import *


class CollectorString(Collector):
    def logic(self):
        return ["Hello", "Hello", "Hello"]


class CollectStringABC(Collector):
    def logic(self):
        return ["a", "b", "c"]


# validate string
class ValidatorSameStrings(Validator):
    # are all instances equal to each other?
    # if we only get the data then we cant check this. so get the datanodes
    required_type = str

    def _validate_data_node(self, data_node):
        inst_wrappers = data_node.parent.data_nodes
        for inst_wrapper in inst_wrappers:
            if inst_wrapper.data != inst_wrappers[0].data:
                raise Exception('Not all instances are equal')

class ValidatorStringIsA(Validator):
    required_type = str

    def logic(self, data):
        assert data == "a"


def test_all_instances_equal():
    # test success
    session = Session()
    session.nodes.append(CollectorString)
    session.nodes.append(ValidatorSameStrings)
    session.run()
    collector = session.node_instances[0]
    assert collector.data_nodes[0].state == NodeState.SUCCEED
    assert collector.data_nodes[1].state == NodeState.SUCCEED
    assert collector.data_nodes[2].state == NodeState.SUCCEED
    print(session.report())

    # test fail
    session = Session()
    session.nodes.append(CollectStringABC)
    session.nodes.append(ValidatorSameStrings)
    session.run()

    assert session.node_instances[0].data_nodes[0].state == NodeState.FAIL
    print(session.report())


def test_failed_result_node():
    """test if a failed result node_result, leads to a failed validation, and a failed data node"""
    session = Session()
    session.add(CollectStringABC)
    session.add(ValidatorStringIsA)
    session.run()

    # print(session.report())

    # print(session.report())
    validator = session.node_instances[1]
    result_node_a, result_node_b, result_node_c = validator.children

    # nodes A B C
    # node 0 should succeed, the rest should fail

    # check if a failed result node results in a failed validation
    assert validator.state == NodeState.FAIL
    assert result_node_a.state == NodeState.SUCCEED
    assert result_node_b.state == NodeState.FAIL
    assert result_node_c.state == NodeState.FAIL
    assert result_node_a.data_node.state == NodeState.SUCCEED
    assert result_node_b.data_node.state == NodeState.FAIL
    assert result_node_c.data_node.state == NodeState.FAIL

    # now we force the state to succeed, and check if the validator state is also succeed
    result_node_b.state = NodeState.SUCCEED
    result_node_c.state = NodeState.SUCCEED
    assert validator.state == NodeState.SUCCEED
    assert result_node_b.data_node.state == NodeState.SUCCEED
    assert result_node_c.data_node.state == NodeState.SUCCEED

    # print(session.report())


class CollectorInts(Collector):
    def logic(self):
        return [1, 2, 3]


# todo test validate incompatible types
def test_incompatible_types():
    session = Session()
    session.add(CollectorString)
    session.add(CollectorInts)
    session.add(ValidatorSameStrings)
    session.run()

    validator = session.node_instances[2]
    print(session.report())


if __name__ == '__main__':
    test_failed_result_node()