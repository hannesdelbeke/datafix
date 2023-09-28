#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import signal
import sys
import Qt
from Qt import QtCore, QtWidgets
from NodeGraphQt import NodeGraph, PropertiesBinWidget, NodesTreeWidget, NodesPaletteWidget

# import example nodes from the "example_nodes" package
from nodes import basic_nodes, callable_node, group_node, widget_nodes
from pac2 import ProcessNode
import pac2.node
from nodes.callable_node import CallableNodeBase


if __name__ == '__main__':

    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication(sys.argv + ['-platform', 'windows:darkmode=2'])

    # create graph controller.
    graph = NodeGraph()

    # set up context menu for the node graph.
    graph.set_context_menu_from_file('../examples/hotkeys/hotkeys.json')

    # todo register pac nodes
    # registered example nodes.
    node_classes = [
        # callable_node.CallableNodeBase,
        group_node.MyGroupNode,
        widget_nodes.TextInputNode,
        widget_nodes.CheckboxNode,
    ]

    class PrintStrings(ProcessNode):
        def __init__(self):
            super().__init__()
            self.string_1: str = "DEFAULT1"
            self.string_2: str = "DEFAULT2"
            self.callable = self._print

        def _print(self):
            print(f"str1{self.string_1}, str2{self.string_2}")

    # node_class = callable_node.create_callable_node_class(
    #     PrintStrings, class_name="PrintStrings", node_name="Print String Test"
    # )  # todo
    # node_classes.append(node_class)

    def print_strings2(str1=2, str2=None):
        import time

        # graph.widget.repaint() # todo move
        time.sleep(1)
        print(f"str1{str1}, str2{str2}")
        # graph.widget.repaint() # todo move

    pac_node_class = pac2.node.node_model_from_callable(print_strings2)
    node_class = ProcessNode.class_from_callable(pac_node_class())
    node_class2 = callable_node.create_callable_node_class(
        node_class, class_name="PrintStrings2", node_name="Print String Test2"
    )  # todo
    node_classes.append(node_class2)

    import pac2.nodes

    for node_class in pac2.Node._node_classes:
        name = node_class.__name__.split("_callable")[0]
        node_class2 = callable_node.create_callable_node_class(
            node_class, class_name=name, identifier="operators"
        )  # todo
        node_classes.append(node_class2)

    data_map = {
        "Int": 0,
        "Float": 0.0,
        "Bool": False,
        "Str": "",
        "List": [],
        "Dict": {},
        "Tuple": (),
        "Set": set(),
        "None": None,
    }
    for key, default_value in data_map.items():

        class _DataNode(pac2.Node):
            def __init__(self):
                super().__init__()
                self.data = 0

        _DataNode.__name__ = key  # + "Node"

        node_class2 = callable_node.create_callable_node_class(_DataNode, identifier="datanodes")  # todo
        node_classes.append(node_class2)

    class FloatNode(pac2.Node):
        def __init__(self):
            super().__init__()
            self.data = 0.0

    class BoolNode(pac2.Node):
        def __init__(self):
            super().__init__()
            self.data = False

    class StrNode(pac2.Node):
        def __init__(self):
            super().__init__()
            self.data = ""

    class ListNode(pac2.Node):
        def __init__(self):
            super().__init__()
            self.data = []

    class DictNode(pac2.Node):
        def __init__(self):
            super().__init__()
            self.data = {}

    class TupleNode(pac2.Node):
        def __init__(self):
            super().__init__()
            self.data = ()

    class SetNode(pac2.Node):
        def __init__(self):
            super().__init__()
            self.data = set()

    class NoneNode(pac2.Node):
        def __init__(self):
            super().__init__()
            self.data = None

    print("node_classes", [x.__name__ for x in ProcessNode._node_classes])
    # print("node_class", node_class)

    # print("node_class2", type(pac_node), pac_node, dir(pac_node))
    # print(dir(pac_node()))
    # n = pac_node()
    # print("RUN")
    # n()
    # print("RUN")
    graph.register_nodes(node_classes)

    # show the node graph widget.
    graph_widget = graph.widget
    graph_widget.resize(1100, 800)
    # graph_widget.show()

    # create node with the custom port shapes.
    process_node = graph.create_node('nodes.callable.PrintStrings2')
    process_node2 = graph.create_node('nodes.callable.PrintStrings2')

    process_node2.set_input(0, process_node.output(0))  # todo
    # (connect nodes using the .connect_to method from the port object)

    # auto layout nodes.
    graph.auto_layout_nodes()

    # fit nodes to the viewer.
    graph.clear_selection()
    graph.fit_to_selection()

    # Custom builtin widgets from NodeGraphQt
    # ---------------------------------------

    # create a node properties bin widget.
    properties_bin = PropertiesBinWidget(node_graph=graph)
    properties_bin.setWindowFlags(QtCore.Qt.Tool)

    # example show the node properties bin widget when a node is double clicked.
    def display_properties_bin(node):
        if not properties_bin.isVisible():
            properties_bin.show()

    # wire function to "node_double_clicked" signal.
    graph.node_double_clicked.connect(display_properties_bin)

    # create a nodes tree widget.
    nodes_tree = NodesTreeWidget(node_graph=graph)
    nodes_tree.set_category_label('nodeGraphQt.nodes', 'Builtin Nodes')
    nodes_tree.set_category_label('nodes.callable', 'Callable Nodes')
    nodes_tree.set_category_label('nodes.widget', 'Widget Nodes')
    nodes_tree.set_category_label('nodes.basic', 'Basic Nodes')
    nodes_tree.set_category_label('nodes.group', 'Group Nodes')
    # nodes_tree.show()

    widget = QtWidgets.QMainWindow()

    dock_tree = QtWidgets.QDockWidget()
    dock_tree.setWidget(nodes_tree)

    # reset background color for category items stuck in white
    for category, item in nodes_tree._category_items.items():
        item.setBackground(0, QtCore.Qt.NoBrush)

    # add a button under the node tree to create a new node.
    btn = QtWidgets.QPushButton('PROCESS NODES')
    # set green, set text color black
    btn.setStyleSheet("background-color: rgb(100, 180, 50); color: rgb(0, 0, 0);")

    #
    def process_nodes():

        import pac2

        for n in pac2.Node._nodes.values():
            n.dumb_disconnect_all()

        # get connections from view, and transfer to model
        data = graph.serialize_session()
        # {
        #   "out":[
        #     "0x23d30810eb0",
        #     "out"
        #   ],
        #   "in":[
        #     "0x23d30813c70",
        #     "in"
        #   ]
        # },
        for connection in data.get("connections", []):
            node_in_id, slot_in_name = connection["in"]
            node_out_id, slot_out_name = connection["out"]

            # get [VIEW node out] with node_out_id
            qt_node_out = graph.get_node_by_id(node_out_id)
            qt_node_in = graph.get_node_by_id(node_in_id)
            # get pac node in the [VIEW node out]
            pac_node_out = qt_node_out._callable_node
            pac_node_in = qt_node_in._callable_node
            # connect pac node to pac node in [VIEW node in]
            pac_node_out.connect(pac_node_in, slot_out_name, slot_in_name)

        for node_id, node in graph.model.nodes.items():
            if isinstance(node, CallableNodeBase):
                # get node connected to IN slot
                ports = node.inputs()["CALL"].connected_ports()
                if ports:
                    in_node = ports[0].node()
                    print("IN NODE", in_node)
                    in_node.start()
                else:
                    node.start()

                return  # only run 1 node, which should triggert the next nodes. # todo

    btn.clicked.connect(process_nodes)
    dock_btn = QtWidgets.QDockWidget()
    dock_btn.setWidget(btn)

    widget.setCentralWidget(graph_widget)
    widget.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_tree)
    widget.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_btn)
    widget.show()

    # app = QApplication(sys.argv + ['-platform', 'windows:darkmode=2'])
    # app.setStyle('Fusion')
    # app.setPalette(get_darkModePalette(app))

    # from qt_material import apply_stylesheet
    # apply_stylesheet(app, theme='dark_amber.xml')
    # import unreal_stylesheet
    # unreal_stylesheet.setup(app)

    import qdarktheme

    qdarktheme.setup_theme()
    app.exec_()
