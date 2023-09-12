from pac2 import ProcessNode

import pac_sample.my_blender_api.collect_objects  # todo delay import

node = ProcessNode(callable=pac_sample.my_blender_api.collect_objects.main)
