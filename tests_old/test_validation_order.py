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
    """
    if a datanode's 1st validation fails & the 2nd validation succeeds,
    the datanode state should stay fail, and not overwritten by the 2nd succeed
    """
    session = Session()
    session.nodes.append(CollectHelloWorld)
    session.nodes.append(ValidateFail)
    session.nodes.append(ValidateSuccess)
    session.run()
    # print(session.report())
    assert session.node_instances[0].data_nodes[0].state == NodeState.FAIL


if __name__ == '__main__':
    test_validation_order()
