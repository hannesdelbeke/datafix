from pac.logic import *


# use case:
# artist runs a validation pipeline on their 3d scene
# the tool finds an issue with a mesh and informs the artist
# the artist fixes the mesh, and wants to re-validate the mesh, without having to revalidate the whole scene.
# (since depending on the pipeline this could take a long time)

# run whole pipeline
# then revalidate a node


# collect string
class CollectString(Collector):
    def _run(self):
        return ["Hello World"]


# validate string
class ValidateString(Validator):
    def validate_instance(self, instance):
        assert instance == "changed"


def test_revalidate_instance():
    session = Session()
    session.registered_plugins.append(CollectString)
    session.registered_plugins.append(CollectString)
    session.registered_plugins.append(ValidateString)
    session.run()
    session.pp_tree()

    # collector1 -> collects instance 1 'Hello World'
    # collector2 -> collects instance 2 'Hello World'
    # validator -> validates instance 1 & 2, both fail
    # we now 'fix' the instance 1, and revalidate the instance 1
    collector_1 = session.plugin_instances[0]
    instance_wrap_1 = collector_1.instance_wrappers[0]
    instance_wrap_1.instance = "changed"

    collector_2 = session.plugin_instances[1]
    instance_wrap_2 = collector_2.instance_wrappers[0]

    # TODO move this to node function
    # get connections: nodes that ran on this instance (aka validators)
    # BUG we loop through connections, but validate_instance_wrapper adds a connection during loop
    connected_nodes = instance_wrap_1.connections[:]
    for connected_node in connected_nodes:

        # get result entry in connected node, delete old result
        # connected_node.results == [[InstanceWrapper(Hello World), 'failed'], [InstanceWrapper(changed), 'failed']]
        for result in connected_node.results:
            if result[0] == instance_wrap_1:
                connected_node.results.remove(result)
                break

        connected_node.validate_instance_wrapper(instance_wrap_1)
        # connected_node.results == [[InstanceWrapper(Hello World), 'failed'], [InstanceWrapper(changed), 'success']]

    assert instance_wrap_1.state == 'success'
    assert instance_wrap_2.state != 'success'
