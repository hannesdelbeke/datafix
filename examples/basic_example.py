#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import signal

import Qt
from Qt import QtCore, QtWidgets

from NodeGraphQt import NodeGraph, PropertiesBinWidget, NodesTreeWidget, NodesPaletteWidget

# import example nodes from the "example_nodes" package
from nodes import basic_nodes, callable_node, group_node, widget_nodes

if __name__ == '__main__':

    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])

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
    ]

    from pac2 import ProcessNode

    class PrintStrings(ProcessNode):
        def __init__(self):
            super().__init__()
            self.string_1: str = "DEFAULT1"
            self.string_2: str = "DEFAULT2"
            self.callable = self._print

        def _print(self):
            print(f"str1{self.string_1}, str2{self.string_2}")

    node_class = callable_node.create_callable_node_class(PrintStrings, class_name="PrintStrings")  # todo
    node_classes.append(node_class)
    graph.register_nodes(node_classes)

    # show the node graph widget.
    graph_widget = graph.widget
    graph_widget.resize(1100, 800)
    # graph_widget.show()

    # create node with the custom port shapes.
    process_node = graph.create_node('nodes.callable.PrintStrings')
    process_node2 = graph.create_node('nodes.callable.PrintStrings')

    # create group node.
    n_group = graph.create_node('nodes.group.MyGroupNode', color=(100, 100, 100))

    process_node2.set_input(0, process_node.output(0))  # todo
    # (connect nodes using the .connect_to method from the port object)

    # todo automate hookup based on view
    # process_node2._callable_node.IN = process_node._callable_node
    process_node._callable_node.OUT = process_node2._callable_node
    print("input_nodes", process_node2._callable_node, "---", process_node2._callable_node.input_nodes)

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

    # add a button under the node tree to create a new node.
    btn = QtWidgets.QPushButton('PROCESS NODES')
    # set green
    btn.setStyleSheet("background-color: rgb(150, 255, 60);")
    from nodes.callable_node import CallableNodeBase

    #
    def test():
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

    btn.clicked.connect(test)
    dock_btn = QtWidgets.QDockWidget()
    dock_btn.setWidget(btn)

    widget.setCentralWidget(graph_widget)
    widget.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_tree)
    widget.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_btn)
    widget.show()

    app.exec_()
