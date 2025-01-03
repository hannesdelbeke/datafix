from pac.logic import *


class CollectString(Collector):
    def logic(self):
        return ["Hello", "Hello", "Hello"]


class CollectStringFail(Collector):
    def logic(self):
        return ["a", "b", "c"]


# validate string
class ValidateString(Validator):
    # TODO def to validate multiple instances relative to each other

    # def validate_instance(self, instance):
    # are all instances equal to each other?
    # if we only get instance then we cant check this.

    def _validate_data_node(self, data_node):
        inst_wrappers = data_node.parent.data_nodes
        for inst_wrapper in inst_wrappers:
            if inst_wrapper.data != inst_wrappers[0].data:
                raise Exception('Not all instances are equal')


def test_all_instances_equal():
    session = Session()
    session.nodes.append(CollectString)
    session.nodes.append(ValidateString)
    session.run()

    assert session.node_instances[0].data_nodes[0]._state == NodeState.SUCCEED
    assert session.node_instances[0].data_nodes[1]._state == NodeState.SUCCEED
    assert session.node_instances[0].data_nodes[2]._state == NodeState.SUCCEED

    session = Session()
    session.nodes.append(CollectStringFail)
    session.nodes.append(ValidateString)
    session.run()

    assert session.node_instances[0].data_nodes[0]._state == NodeState.FAIL
