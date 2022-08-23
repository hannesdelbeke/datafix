from pac.logic import *


class StringToIntAdapter(Adapter):
    # input: instance of type string
    # output: instance of type int
    type_input = str
    type_output = int

    def _run(self, instance: str):
        magic_dict = {
            'zero': 0,
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
        }
        return magic_dict.get(instance, instance)  # return instance if we cant convert


class IntToStringAdapter(Adapter):
    # input: instance of type int
    # output: instance of type string
    type_input = int
    type_output = str

    def _run(self, instance):
        return str(instance)


# an action that takes a string, and uppercases it
class ActionUppercase(Action):
    def _run(self):
        return self.input.upper()


class CollectNumbers(Collector):
    def _run(self):
        # return [1, 2, 3]
        return [1]


class CollectStringNumbers(Collector):
    def _run(self):
        # return ["one", "two", "three"]
        return ["one"]


class ValidateNumbers(Validator):
    required_type = int

    def validate_instance(self, instance):
        assert type(instance) == int


def test_adapter():
    adapterBrain = AdapterBrain()
    adapterBrain.register_adapter(StringToIntAdapter())
    adapterBrain.register_adapter(IntToStringAdapter())

    session = Session()
    session.adapter_brain = adapterBrain

    session.registered_plugins.append(CollectNumbers)
    session.registered_plugins.append(CollectStringNumbers)
    session.registered_plugins.append(ValidateNumbers)
    session.run()

    # get both instances
    assert session.plugin_instances[0].instance_wrappers[0].state == 'success'
    assert session.plugin_instances[1].instance_wrappers[0].state == 'success'
