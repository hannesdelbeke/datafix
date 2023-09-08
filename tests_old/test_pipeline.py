from pac.logic import *


class CollectHelloWorld(Collector):
    def _run(self):
        return ["Hello World"]


class CollectHelloWorldList(Collector):
    def _run(self):
        return ["Hello", "World"]


class ValidateHelloWorld(Validator):
    def validate_instance(self, instance):
        assert instance == "Hello World"


def test_simple_session2():
    session = Session()
    session.registered_plugins.append(CollectHelloWorld)
    session.registered_plugins.append(CollectHelloWorld)
    session.registered_plugins.append(CollectHelloWorldList)
    session.registered_plugins.append(ValidateHelloWorld)
    # session.run()

    import pac.pipeline
    import pprint

    pprint.pprint(session.__dict__)
    dct = pac.pipeline.NodeJSONEncoder().encode(session)
    import json

    dct = json.loads(dct)

    pprint.pprint(dct, indent=4)


test_simple_session2()
