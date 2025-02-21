from datafix.logic import *


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
    return session


if __name__ == '__main__':
    s = test_simple_session2()
    print(s.state)