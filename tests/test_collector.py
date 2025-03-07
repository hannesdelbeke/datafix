from datafix.core import Session, Collector, NodeState


# test that we can collect a string
class CollectHelloWorld(Collector):
    def collect(self):
        return ["Hello World"]


def test_single_collect():
    """test we can collect a data_node from a collector node"""
    session = Session()
    session.append(CollectHelloWorld)
    session.run()
    assert session.state == NodeState.SUCCEED
    assert session.children[0].data_nodes[0].data == "Hello World"


# test we can collect 2 strings
class CollectHelloWorldList(Collector):
    def collect(self):
        return ["Hello", "World"]


def test_double_collect():
    """test we can collect 2 data_nodes from 1 collector node"""
    session = Session()
    session.append(CollectHelloWorldList)
    session.run()
    print(session.report())

    assert session.state == NodeState.SUCCEED
    assert session.children[0].data_nodes[0].data == "Hello"
    assert session.children[0].data_nodes[1].data == "World"


def test_collect_twice():
    session = Session()
    collector = CollectHelloWorld(parent=session)
    session.run()
    assert len(collector.children) == 1
    session.run()
    assert len(collector.children) == 1

# test that we can fail to collect due to exception, and continue to next node
class CollectFail(Collector):
    def collect(self):
        raise Exception('Force raise exception')


def test_fail_collect():
    """test the Collector node can fail, and the session will continue to the next node"""
    session = Session()
    session.append(CollectFail)
    session.append(CollectHelloWorld)
    session.run()
    print(session.report())
    assert session.state == NodeState.FAIL
    assert session.children[0].state == NodeState.FAIL
    assert session.children[1].state == NodeState.SUCCEED
    assert session.children[0].data_nodes == []  # failed to collect dataNode
    assert session.children[1].data_nodes[0].data == "Hello World"


# def test_fail_warning_collect() -> Session:
#     session = Session()
#     session.add(CollectFail)
#     session.add(CollectHelloWorld)
#     CollectHelloWorld.continue_on_fail = True  # same as allow fail?
#     session.run()
#     assert session.state == NodeState.WARNING
#     assert session.node_instances[0].state == NodeState.WARNING
#     assert session.node_instances[1].state == NodeState.SUCCEED
#     return session


if __name__ == '__main__':
    test_single_collect()
    test_double_collect()
    test_fail_collect()
    # test_fail_warning_collect()
