from pac2 import ProcessNode


class CollectObjects(ProcessNode):
    def __init__(self):
        import pac_sample.my_blender_api.collect_objects  # delay import
        super().__init__(callable=pac_sample.my_blender_api.collect_objects.main)
