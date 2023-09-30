import logging

import pac2.node


# def create_cube():
#     bpy.ops.mesh.primitive_cube_add()
# # def create_


import ast


def extract_kwargs(text):
    # Extract arguments as a string
    arguments_str = text.split("(", 1)[1].rsplit(")", 1)[0]

    # Parse arguments as an abstract syntax tree
    arguments_ast = ast.parse(f"temp_func({arguments_str})", mode="eval")

    # Extract variable names and values from the abstract syntax tree
    variables = []
    for node in ast.walk(arguments_ast):
        if isinstance(node, ast.keyword):
            var_name = node.arg
            var_value = ast.literal_eval(node.value)
            variables.append((var_name, var_value))

    return variables


import logging

import bpy

for attr_name in dir(bpy.ops.mesh):
    attr = getattr(bpy.ops.mesh, attr_name)
    # print(attr, type(attr))
    # check if callable
    if not callable(attr):
        logging.warning(f"attr '{attr_name}' is not callable, can't make node")
        continue
    if attr_name.startswith("_"):
        logging.warning(f"attr '{attr_name}' is private, skip node")
        continue

    # if not callable(getattr(bpy.ops.mesh, attr)):
    node_model_class = pac2.node.node_model_class_from_callable(attr, model_name=attr._func)

    node_model = node_model_class()

    try:
        kwargs = extract_kwargs(attr.__doc__.split("/n")[0].strip())
        for key, value in kwargs:
            node_model._default_map_[key] = value
        # remove args and kwargs from _default_map_
        node_model._default_map_.pop("args")
        node_model._default_map_.pop("kw")
    except Exception as e:
        logging.warning(e)
        print("docstring", attr.__doc__)

    # print("node_model", node_model, dir(node_model))

    node = pac2.ProcessNode.class_from_callable(node_model)


# node_model_class = pac2.node.node_model_class_from_callable(extract_kwargs)
# node_model = node_model_class()
# node_model._default_map_["test_var"] = 1
# node = pac2.ProcessNode.class_from_callable(node_model)
