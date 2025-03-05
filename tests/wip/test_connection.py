from datafix import Session
from datafix import Validator


# session
#   collect_node
#     instance A
#     instance B
#   validator_node
#     validate A SUCCESS
#     validate B FAIL

# connection instance A -> validator A, result SUCCESS
# connection instance B -> validator A, result FAIL


class CollectA(Collector):
    def run(self):
        return ["A"]


class CollectB(Collector):
    def run(self):
        return ["B"]


class ValidatorAB(Validator):

    # normally we don't override validate_instance, but validate_instance_node instead
    # but to isolate wrapper logic for testing we override validate_instance directly
    def logic(self, data):
        assert data == "A"


def test_simple_session():
    session = Session()
    session.add(CollectA)
    session.add(CollectB)
    session.add(ValidatorAB)
    session.run()
    return session


if __name__ == '__main__':
    session = test_simple_session()
