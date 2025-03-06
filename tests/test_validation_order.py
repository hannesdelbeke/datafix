from datafix.core import Session, NodeState, Collector, Validator


class CollectHelloWorld(Collector):
    def collect(self):
        return ["Hello World"]


class ValidateSuccess(Validator):
    def validate(self, data):
        pass


class ValidateFail(Validator):
    def validate(self, data):
        raise Exception('Fail')


def test_validation_order():
    """
    if a datanode's 1st validation fails & the 2nd validation succeeds,
    the datanode state should stay fail, and not overwritten by the 2nd succeed
    """
    session = Session()
    session.append(CollectHelloWorld)
    session.append(ValidateFail)
    session.append(ValidateSuccess)
    session.run()
    # print(session.report())
    assert session.children[0].data_nodes[0].state == NodeState.FAIL


if __name__ == '__main__':
    test_validation_order()
