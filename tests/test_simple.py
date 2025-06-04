from datafix.core import Collector, Validator, active_session, Action

"""
1. Define your Collectors.

Collectors should always return a list of data.
These then automatically create data nodes for each list item they return. 

e.g. these collectors return a list of strings.
the first collector creates a datanode containing the value "hello world"
the 2nd collector creates 2 datanodes, one with the value "hello" and one with "world" 
"""


class CollectHelloWorld(Collector):
    def collect(self):
        return ["Hello World"]


class CollectHelloWorldList(Collector):
    def collect(self):
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

    def validate(self, data):
        assert data == "Hello World", "Data is not 'Hello World'"


class ValidateContainsHello(Validator):
    def validate(self, data):
        assert "Hello" in data, "Data does not contain 'Hello'"

"""
3. Define the pipeline

Now that you defined the building blocks of your pipeline, 
it's time to hook it all up.
we use datafix.active_session
First we register the collectors, to collect our datanodes.
Then we register the validators, which will run on our collected datanodes.
When you have your first pipeline defined, you can run it with 
"""


def setup_sample_pipeline():
    class ActionPrintNode(Action):
        def run(self):
            print(self.parent)

    # create a collector node
    collector_node = CollectHelloWorld(parent=active_session)
    # add a instanced action to the collector node
    collector_node.actions.append(ActionPrintNode(parent=collector_node))
    # tell the collector, to add the ActionPrintNode to every child node it creates
    collector_node.child_actions.append(ActionPrintNode)

    active_session.append(CollectHelloWorldList)
    active_session.append(ValidateHelloWorld)
    active_session.append(ValidateContainsHello)


def test_simple_session2():
    setup_sample_pipeline()
    active_session.run()
