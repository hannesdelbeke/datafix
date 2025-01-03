from pac.logic import *


class CollectHelloWorld(Collector):
    def logic(self):
        return ["Hello World"]


class ValidateSuccess(Validator):
    def logic(self, data):
        pass


class ValidateFail(Validator):
    def logic(self, data):
        raise Exception('Fail')


def test_validation_order():
    session = Session()
    session.nodes.append(CollectHelloWorld)
    session.nodes.append(ValidateFail)
    session.nodes.append(ValidateSuccess)
    session.run()

    # if we first succeed, then fail validation, then instance wrap state should fail
    assert session.node_instances[0].data_nodes[0]._state == NodeState.FAIL

test_validation_order()