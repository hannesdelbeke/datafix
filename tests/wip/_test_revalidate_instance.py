from datafix.core import Session, Validator, Collector, NodeState


# use case for revalidating (running the validator twice):
# artist runs a validation pipeline on their 3d scene
# datafix informs the artist of an issue with a mesh
# the artist fixes the mesh, and wants to re-validate the mesh without revalidating the whole scene.
# (since this could take a long time)

# run whole pipeline
# then revalidate a node


class CollectString(Collector):
    def collect(self):
        return ["Helo Werld"]


class ValidateSpelling(Validator):
    def validate(self, data):
        assert data == "Hello World"


def test_revalidate_instance():
    # register 2 collectors and 1 validator
    session = Session()
    session.append(CollectString)
    session.append(CollectString)
    session.append(ValidateSpelling)

    session.run()
    # collector1 -> collects instance 1 'Helo Werld'
    # collector2 -> collects instance 2 'Helo Werld'
    # validator -> validates instance 1 & 2, both fail

    # we now 'fix' the instance 1, and revalidate the instance 1
    collector_1 = session.children[0]
    instance_wrap_1 = collector_1.data_nodes[0]
    instance_wrap_1.data = "Hello World"

    collector_2 = session.children[1]
    instance_wrap_2 = collector_2.data_nodes[0]

    # TODO move this to node function
    # get connections: nodes that ran on this instance (aka validators (TODO but also result nodes)
    # BUG we loop through connections, but validate_instance_node adds a connection during loop
    connected_nodes = instance_wrap_1.connections[:]
    for connected_node in connected_nodes:

        # get result entry in connected node, delete old result
        # connected_node.results == [[InstanceWrapper(Hello World), 'failed'], [InstanceWrapper(changed), 'failed']]
        for result in connected_node.results:
            if result[0] == instance_wrap_1:
                connected_node.results.remove(result)
                break

        connected_node.validate_data_node(instance_wrap_1)
        # connected_node.results == [[InstanceWrapper(Hello World), 'failed'], [InstanceWrapper(changed), 'success']]

    assert instance_wrap_1._state == NodeState.SUCCEED
    assert instance_wrap_2._state == NodeState.FAIL

    return session


if __name__ == '__main__':
    session = test_revalidate_instance()

