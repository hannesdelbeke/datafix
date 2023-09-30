# default nodes

import pac2.node


# class AndModel(pac2.node.NodeModelBase):
#     def __init__(self):
#         super().__init__()
#         self.in_1 = None
#         self.in_2 = None
#
#     def __call__(self):
#         return self.in_1 and self.in_2
import pac2.node


def and_callable(a, b):
    return a and b


def or_callable(a, b):
    return a or b


def eq_callable(a, b):
    return a == b


def ne_callable(a, b):
    return a != b


def not_callable(a):
    return not a


def str_callable(a):
    return str(a)


def print_callable(text, *args, **kwargs):
    print(text, *args, **kwargs)


def wait_callable(seconds):
    import time

    time.sleep(seconds)


def add_callable(a, b):
    return a + b


def sub_callable(a, b):
    return a - b


def lt_callable(a, b):
    return a < b


def gt_callable(a, b):
    return a > b


def ge_callable(a, b):
    return a >= b


def le_callable(a, b):
    return a <= b


def is_callable(a, b):
    return a is b


def is_not_callable(a, b):
    return a is not b


def in_callable(a, b):
    return a in b


def not_in_callable(a, b):
    return a not in b


def bitwise_and_callable(a, b):
    return a & b


def bitwise_or_callable(a, b):
    return a | b


def bitwise_xor_callable(a, b):
    return a ^ b


def bitwise_not_callable(a):
    return ~a


def left_shift_callable(a, b):
    return a << b


def right_shift_callable(a, b):
    return a >> b


# create node models from callables
AndModel = pac2.node.node_model_class_from_callable(and_callable)
OrModel = pac2.node.node_model_class_from_callable(or_callable)
EqModel = pac2.node.node_model_class_from_callable(eq_callable)
NeModel = pac2.node.node_model_class_from_callable(ne_callable)
NotModel = pac2.node.node_model_class_from_callable(not_callable)
StrModel = pac2.node.node_model_class_from_callable(str_callable)
PrintModel = pac2.node.node_model_class_from_callable(print_callable)
WaitModel = pac2.node.node_model_class_from_callable(wait_callable)
AddModel = pac2.node.node_model_class_from_callable(add_callable)
SubModel = pac2.node.node_model_class_from_callable(sub_callable)
LtModel = pac2.node.node_model_class_from_callable(lt_callable)
GtModel = pac2.node.node_model_class_from_callable(gt_callable)
GeModel = pac2.node.node_model_class_from_callable(ge_callable)
LeModel = pac2.node.node_model_class_from_callable(le_callable)
IsModel = pac2.node.node_model_class_from_callable(is_callable)
IsNotModel = pac2.node.node_model_class_from_callable(is_not_callable)
InModel = pac2.node.node_model_class_from_callable(in_callable)
NotInModel = pac2.node.node_model_class_from_callable(not_in_callable)
BitwiseAndModel = pac2.node.node_model_class_from_callable(bitwise_and_callable)
BitwiseOrModel = pac2.node.node_model_class_from_callable(bitwise_or_callable)
BitwiseXorModel = pac2.node.node_model_class_from_callable(bitwise_xor_callable)
BitwiseNotModel = pac2.node.node_model_class_from_callable(bitwise_not_callable)
LeftShiftModel = pac2.node.node_model_class_from_callable(left_shift_callable)
RightShiftModel = pac2.node.node_model_class_from_callable(right_shift_callable)

# create processnodes from models
AndNode = pac2.ProcessNode.class_from_callable_class(AndModel)
OrNode = pac2.ProcessNode.class_from_callable_class(OrModel)
EqNode = pac2.ProcessNode.class_from_callable_class(EqModel)
NeNode = pac2.ProcessNode.class_from_callable_class(NeModel)
NotNode = pac2.ProcessNode.class_from_callable_class(NotModel)
StrNode = pac2.ProcessNode.class_from_callable_class(StrModel)
PrintNode = pac2.ProcessNode.class_from_callable_class(PrintModel)
WaitNode = pac2.ProcessNode.class_from_callable_class(WaitModel)
AddNode = pac2.ProcessNode.class_from_callable_class(AddModel)
SubNode = pac2.ProcessNode.class_from_callable_class(SubModel)
LtNode = pac2.ProcessNode.class_from_callable_class(LtModel)
GtNode = pac2.ProcessNode.class_from_callable_class(GtModel)
GeNode = pac2.ProcessNode.class_from_callable_class(GeModel)
LeNode = pac2.ProcessNode.class_from_callable_class(LeModel)
IsNode = pac2.ProcessNode.class_from_callable_class(IsModel)
IsNotNode = pac2.ProcessNode.class_from_callable_class(IsNotModel)
InNode = pac2.ProcessNode.class_from_callable_class(InModel)
NotInNode = pac2.ProcessNode.class_from_callable_class(NotInModel)
BitwiseAndNode = pac2.ProcessNode.class_from_callable_class(BitwiseAndModel)
BitwiseOrNode = pac2.ProcessNode.class_from_callable_class(BitwiseOrModel)
BitwiseXorNode = pac2.ProcessNode.class_from_callable_class(BitwiseXorModel)
BitwiseNotNode = pac2.ProcessNode.class_from_callable_class(BitwiseNotModel)
LeftShiftNode = pac2.ProcessNode.class_from_callable_class(LeftShiftModel)
RightShiftNode = pac2.ProcessNode.class_from_callable_class(RightShiftModel)
