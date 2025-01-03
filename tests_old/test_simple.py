from pac.logic import *


class CollectHelloWorld(Collector):
    def logic(self):
        return ["Hello World"]


class CollectHelloWorldList(Collector):
    def logic(self):
        return ["Hello", "World"]


class ValidateHelloWorld(Validator):
    def logic(self, data):
        assert data == "Hello World"


def test_simple_session2() -> Session:
    session = Session()
    session.nodes.append(CollectHelloWorld)
    session.nodes.append(CollectHelloWorldList)
    session.nodes.append(ValidateHelloWorld)
    session.run()
    session.pp_tree()
    return session

    # wrap_a = session.node_instances[0].data_nodes[0]

s = test_simple_session2()
print(s.state)