from pac2 import ProcessNode

import pac_sample.my_blender_api.validate_object_name  # todo delay import

print(pac_sample.my_blender_api.validate_object_name.main.__name__)
# method __module__ str pac_sample.my_blender_api.validate_object_name
# __name__ str main

node = ProcessNode(callable=pac_sample.my_blender_api.validate_object_name.main)

# node.actions = ["rename", "select"]
