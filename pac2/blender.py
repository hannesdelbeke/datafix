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

MESH = "MESH"
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

    try:
        default_map = {}
        doc_input = attr.__doc__.split("/n")[0].strip()
        doc_input = doc_input.replace("scale=(0, 0, 0)", "scale=(1, 1, 1)")  # fix blender bug
        if "scale" in doc_input:
            print("scale", doc_input)
        kwargs = extract_kwargs(doc_input)
        for key, value in kwargs:
            # node_model._default_map_[key] = value
            default_map[key] = value
            # setattr(node_model, key, value)
            # todo make it so we dont have to both set the default_map and the attribute
        # remove args and kwargs from _default_map_
        # node_model._default_map_.pop("args")
        # node_model._default_map_.pop("kw")
    except Exception as e:
        logging.warning(e)
        print("docstring", attr.__doc__)

    def wrap_blender_hack(*args, **kwargs):
        # with context.temp_override(window=context.window_manager.windows[0]):
        return attr(*args, **kwargs)

    # if not callable(getattr(bpy.ops.mesh, attr)):
    node_model_class = pac2.node.node_model_class_from_callable(attr, model_name=attr._func, default_map=default_map)

    # node_model = node_model_class()

    # print("node_model", node_model, dir(node_model))

    node = pac2.ProcessNode.class_from_callable_class(node_model_class)
    node.__category__ = MESH  # todo set identifier


# node_model_class = pac2.node.node_model_class_from_callable(extract_kwargs)
# node_model = node_model_class()
# node_model._default_map_["test_var"] = 1
# setattr(node_model, "test_var", 1)
# node = pac2.ProcessNode.class_from_callable(node_model)
