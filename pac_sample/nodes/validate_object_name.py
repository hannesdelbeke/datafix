from pac2 import ProcessNode


class ValidateObjects(ProcessNode):
    def __init__(self):
        import pac_sample.my_blender_api.validate_object_name  # delay import
        super().__init__(callable=pac_sample.my_blender_api.validate_object_name.main)
        # node.actions = ["rename", "select"]
