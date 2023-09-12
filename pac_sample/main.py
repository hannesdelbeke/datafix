from pac_sample import nodes
from pac2 import Node, ProcessNode


from pac2 import ProcessNode

import pac_sample.my_blender_api.validate_object_name  # todo delay import

print(pac_sample.my_blender_api.validate_object_name.main.__name__)
# method __module__ str pac_sample.my_blender_api.validate_object_name
# __name__ str main

node = ProcessNode(callable=pac_sample.my_blender_api.validate_object_name.main)

# node.actions = ["rename", "select"]


def register_node_folder(folder_path):
    pass


# register pac modules / nodes / folder
pac.manager.register_node_module(nodes)
pac.manager.collect()  # runs collection on all registered modules
pac.manager.validate()  # runs validation on all registered modules
