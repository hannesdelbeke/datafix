from datafix import *
from datafix import Session
from datafix import Validator


class StringToIntAdapter(Adapter):
    # input: instance of type string
    # output: instance of type int
    type_input = str
    type_output = int

    def logic(self, data: str):
        magic_dict = {
            'zero': 0,
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
        }
        return magic_dict.get(data, data)  # return instance if we cant convert


class IntToStringAdapter(Adapter):
    # input: instance of type int
    # output: instance of type string
    type_input = int
    type_output = str

    def logic(self, data):
        return str(data)


# an action that takes a string, and uppercases it
class ActionUppercase(Action):
    def logic(self):
        return self.input.upper()


class CollectNumbers(Collector):
    def logic(self):
        # return [1, 2, 3]
        return [1]


class CollectStringNumbers(Collector):
    def logic(self):
        # return ["one", "two", "three"]
        return ["one"]


class ValidateNumbers(Validator):
    required_type = int

    def logic(self, data):
        assert type(data) == int


def test_adapter():
    session = Session()
    session.register_adapter(StringToIntAdapter())
    session.register_adapter(IntToStringAdapter())

    session.add(CollectNumbers)
    session.add(CollectStringNumbers)
    session.add(ValidateNumbers)
    session.run()

    # get both instances
    int_numbers = session.children[0]
    string_numbers = session.children[1]
    assert int_numbers.data_nodes[0]._state == NodeState.SUCCEED
    assert string_numbers.data_nodes[0]._state == NodeState.SUCCEED

    print(session.report())


if __name__ == '__main__':
    test_adapter()