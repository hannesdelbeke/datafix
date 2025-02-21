from datafix.logic import *


"""
1. Define your Collectors.

Collectors should always return a list of data.
These then automatically create data nodes for each list item they return. 

e.g. these collectors return a list of strings.
the first collector creates a datanode containing the value "hello world"
the 2nd collector creates 2 datanodes, one with the value "hello" and one with "world" 
"""


class CollectHelloWorld(Collector):
    def logic(self):
        return ["Hello World"]


class CollectHelloWorldList(Collector):
    def logic(self):
        return ["Hello", "World"]


"""
2. Define your Validators

The easiest way to create a validator, is to inherit from datafix.Validator
and create a method called logic with an arg 'data'
The values from the collector are passed to data
These can then be used by your validation logic.
"""


class ValidateHelloWorld(Validator):
    warning = True

    def logic(self, data):
        assert data == "Hello World"


"""
3. 

Now that you defined the building blocks of your pipeline, 
it's time to hook it all up.
we use datafix.active_session
First we register the collectors, to collect our datanodes.
Then we register the validators, which will run on our collected datanodes.
When you have your first pipeline defined, you can run it with 
"""

def test_simple_session2() -> Session:
    active_session.add(CollectHelloWorld)
    active_session.add(CollectHelloWorldList)
    active_session.add(ValidateHelloWorld)
    # active_session.run()


if __name__ == '__main__':
    test_simple_session2()

    # this prints the state of the session.
    # success means the session ran successfully,
    # it doesn't mean all data nodes passed validation!

    # print a report with colored output on succeed or fail
    # for each collector and datanode
    print(active_session.report())

    import ui_demo.validator

    ui_demo.validator.show()