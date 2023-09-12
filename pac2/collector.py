from pac2 import Node


class ValidatorCollector(Node):
    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_modules = []


# def collect_validator_nodes():
#     validate_nodes = list(Node.iter_nodes_from_submodules(pac2.validators.deepnest))
