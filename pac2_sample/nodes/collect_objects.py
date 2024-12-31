from pac2 import ProcessNode


class CollectObjects(ProcessNode):
    def __init__(self):
        import pac2_sample.my_blender_api.collect_objects  # delay import
        super().__init__(callable=pac2_sample.my_blender_api.collect_objects.main)
