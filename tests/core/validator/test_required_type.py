from datafix.core import Collector, Validator, Session, NodeState, ResultNode


class Type1(str):...
class Type2(str):...


class CollectType1(Collector):
    def collect(self):
        return [Type1(name) for name in ["type1 A", "type1 B", "type1 C"]]


class CollectType2(Collector):
    def collect(self):
        return [Type2(name) for name in ["type2 A", "type2 B", "type2 C"]]


class ValidateType1(Validator):
    required_type = Type1

    def validate(self, data):
        # if not, raise exception
        if not data.startswith("type1"):
            raise ValueError(f"Invalid type: {data}")


def test_required_type():
    # create pipeline
    session = Session(name="test_required_type")
    type1_collector = CollectType1(parent=session)
    type2_collector = CollectType2(parent=session)
    type1_validator = ValidateType1(parent=session)

    session.run()

    assert type1_collector.state == NodeState.SUCCEED
    assert type2_collector.state == NodeState.SUCCEED
    assert type1_validator.state == NodeState.SUCCEED
    
    # The validator should only process Type1 data due to required_type filtering
    validated_nodes = [child.data_node for child in type1_validator.children] 
    assert validated_nodes == type1_collector.children