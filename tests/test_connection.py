from pac.port import *

# session
#   collect_node
#     instance A
#     instance B
#   validator_node
#     validate A SUCCESS
#     validate B FAIL

# connection instance A -> validator A, result SUCCESS
# connection instance B -> validator A, result FAIL


class CollecA(Collector):
    def run(self):
        return ["A"]


class CollecB(Collector):
    def run(self):
        return ["B"]


class ValidatorAB(Validator):
    def validate_instance(self, instance):
        assert instance == "A"


def test_simple_session():
    session = Session()
    session.registered_plugins.append(CollecA)
    session.registered_plugins.append(CollecB)
    session.registered_plugins.append(ValidatorAB)
    session.run()

