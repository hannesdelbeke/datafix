from pac2 import ProcessNode, Node, ValidatorNode


class Manager(ProcessNode):
    def __init__(self):
        super().__init__()
        self.stage = "init"


    # def collect_plugins(self):
    #     # collect the nodes used in the pipeline
    #
    #     pass


    def collect_instances(self):
        # collect all instances

        # run all process nodes that are collectors
        # mark results as instances, with families/tags

        self.stage = "collected"
        pass

    def validate(self):

        self.stage = "validated"
        pass

    def export(self):

        self.stage = "exported"
        pass


    def publish(self):
        # self.collect_plugins()

        self.collect_instances()
        self.validate()
        self.export()

