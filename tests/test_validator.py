import logging

from datafix.core import Session, Validator, Collector, NodeState


class CollectorString(Collector):
    def collect(self):
        return ["Hello", "Hello", "Hello"]


class CollectStringABC(Collector):
    def collect(self):
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

    def validate(self, data):
        assert data == "a"


def test_all_instances_equal():
    # test success
    session = Session()
    CollectorString(parent=session)
    session.run()
    collector = session.children[0]
    print(session.report())
    assert collector.data_nodes[0].state == NodeState.SUCCEED
    assert collector.data_nodes[1].state == NodeState.SUCCEED
    assert collector.data_nodes[2].state == NodeState.SUCCEED

    # test fail
    session = Session()
    CollectorString(parent=session)
    ValidatorSameStrings(parent=session)
    session.run()

    assert session.children[0].data_nodes[0].state == NodeState.FAIL
    print(session.report())


def test_failed_result_node():
    """test if a failed result node_result, leads to a failed validation, and a failed data node"""
    session = Session()
    session.append(CollectStringABC)
    session.append(ValidatorStringIsA)
    session.run()

    # print(session.report())
    validator = session.children[1]
    result_node_a, result_node_b, result_node_c = validator.children

    # nodes A B C
    # node 0 should succeed, the rest should fail

    # check if a failed result node results in a failed validation
    assert validator.state == NodeState.FAIL, f"Validator should fail but is {validator.state}"
    assert result_node_a.state == NodeState.SUCCEED
    assert result_node_b.state == NodeState.FAIL
    assert result_node_c.state == NodeState.FAIL
    assert result_node_a.data_node.state == NodeState.SUCCEED
    assert result_node_b.data_node.state == NodeState.FAIL
    assert result_node_c.data_node.state == NodeState.FAIL

    # now we force the state to succeed, and check if the validator state is also succeed
    # result_node_b.state = NodeState.SUCCEED
    # result_node_c.state = NodeState.SUCCEED
    # assert validator.state == NodeState.SUCCEED
    # assert result_node_b.data_node.state == NodeState.SUCCEED
    # assert result_node_c.data_node.state == NodeState.SUCCEED

    # print(session.report())

def test_validate_twice():
    """check we correctly clear the results when we rerun a validator"""
    logging.warning("test")
    session = Session()
    session.append(CollectStringABC)
    validator = ValidatorStringIsA(parent=session)
    session.run()
    length = len(validator.children)
    print("children", validator.children)
    session.run()
    print("children", validator.children)
    assert length == len(validator.children)


class CollectorInts(Collector):
    def collect(self):
        return [1, 2, 3]


# todo test validate incompatible types
def test_incompatible_types():
    session = Session()
    session.append(CollectorString)
    session.append(CollectorInts)
    session.append(ValidatorSameStrings)
    session.run()

    validator = session.children[2]
    print(session.report())


if __name__ == '__main__':
    test_validate_twice()