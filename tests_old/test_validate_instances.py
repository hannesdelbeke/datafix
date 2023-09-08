from pac.logic import *


class CollectString(Collector):
    def _run(self):
        return ["Hello", "Hello", "Hello"]


class CollectStringFail(Collector):
    def _run(self):
        return ["a", "b", "c"]


# validate string
class ValidateString(Validator):
    # TODO def to validate multiple instances relative to each other

    # def validate_instance(self, instance):
    # are all instances equal to each other?
    # if we only get instance then we cant check this.

    def _validate_instance_wrapper(self, instance_wrapper):
        inst_wrappers = instance_wrapper.parent.instance_wrappers
        for inst_wrapper in inst_wrappers:
            if inst_wrapper.instance != inst_wrappers[0].instance:
                raise Exception('Not all instances are equal')


def test_all_instances_equal():
    session = Session()
    session.registered_plugins.append(CollectString)
    session.registered_plugins.append(ValidateString)
    session.run()

    assert session.plugin_instances[0].instance_wrappers[0].state == NodeState.SUCCEED
    assert session.plugin_instances[0].instance_wrappers[1].state == NodeState.SUCCEED
    assert session.plugin_instances[0].instance_wrappers[2].state == NodeState.SUCCEED

    session = Session()
    session.registered_plugins.append(CollectStringFail)
    session.registered_plugins.append(ValidateString)
    session.run()

    assert session.plugin_instances[0].instance_wrappers[0].state == NodeState.FAIL
