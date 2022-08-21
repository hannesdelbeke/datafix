from pac.logic import *


class StringToIntAdapter(Adapter):
    # input: instance of type string
    # output: instance of type int
    type_input = str
    type_output = int

    def _run(self, instance):
        return int(instance)

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

def test_adapter():
    adapterBrain = AdapterBrain()
    adapterBrain.register_adapter(StringToIntAdapter())
    adapterBrain.register_adapter(IntToStringAdapter())

    # run uppercase action on instance of type int
    # action = ActionUppercase(input=adapterBrain.convert(1, type_input=int))
    assert False # TODO


