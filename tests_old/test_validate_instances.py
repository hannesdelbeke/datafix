from pac.logic import *


class CollectorString(Collector):
    def logic(self):
        return ["Hello", "Hello", "Hello"]


class CollectStringFail(Collector):
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
    session.nodes.append(CollectStringFail)
    session.nodes.append(ValidatorSameStrings)
    session.run()

    assert session.node_instances[0].data_nodes[0].state == NodeState.FAIL
    print(session.report())


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
    test_all_instances_equal()

    # set the logging level to info
    logging.basicConfig(level=logging.INFO)

    # test_incompatible_types()