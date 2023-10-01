#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import signal
import sys
import Qt
from Qt import QtCore, QtWidgets
from NodeGraphQt import NodeGraph, PropertiesBinWidget, NodesTreeWidget, NodesPaletteWidget

import pac2

# import example nodes from the "example_nodes" package
from examples.nodes import basic_nodes, callable_node, group_node, widget_nodes
from pac2 import ProcessNode, Node
from pac2.node import node_model_class_from_callable, NodeState

# import pac2.node
from examples.nodes.callable_node import CallableNodeBase

import pac2.nodes

"""
import examples.basic_example as b
b.main()
"""

from Qt.QtWidgets import (
    QApplication,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
    QLineEdit,
    QLabel,
)
import Qt.QtCore


class AttributeEditorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.obj = None
        self.init_ui()

    def init_ui(self):

        layout = QVBoxLayout()
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(['Attribute', 'Value'])
        layout.addWidget(self.table_widget)  # , stretch=1)
        self.setLayout(layout)

        # self.table_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def load_ui(self, obj, attrs=None):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)

        if not obj:
            self.obj = None
            return

        self.obj = obj

        attributes = vars(obj)
        for attribute_name, attribute_value in attributes.items():
            # filter
            if attrs and attribute_name not in attrs:
                continue

            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)

            label_item = QTableWidgetItem(attribute_name)
            self.table_widget.setItem(row_position, 0, label_item)

            edit_widget = self.create_edit_widget(attribute_name, attribute_value)
            self.table_widget.setCellWidget(row_position, 1, edit_widget)

            # disable row if start with _
            if attribute_name.startswith("_"):
                edit_widget.setEnabled(False)
                label_item.setFlags(QtCore.Qt.NoItemFlags)

    def create_edit_widget(self, attribute_name, value):
        if isinstance(value, bool):
            checkbox = QCheckBox()
            checkbox.setChecked(value)
            checkbox.stateChanged.connect(
                lambda state, name=attribute_name: self.update_obj_attribute(name, state == QtCore.Qt.Checked)
            )
            return checkbox
        elif isinstance(value, int):
            line_edit = QtWidgets.QSpinBox()
            line_edit.setValue(value)
            line_edit.editingFinished.connect(
                lambda name=attribute_name, widget=line_edit: self.update_obj_attribute(name, int(widget.text()))
            )
            return line_edit
        elif isinstance(value, str):
            line_edit = QLineEdit()
            line_edit.setText(value)
            line_edit.editingFinished.connect(
                lambda name=attribute_name, widget=line_edit: self.update_obj_attribute(name, widget.text())
            )
            return line_edit
        elif isinstance(value, float):
            line_edit = QtWidgets.QDoubleSpinBox()
            line_edit.setValue(value)
            line_edit.editingFinished.connect(
                lambda name=attribute_name, widget=line_edit: self.update_obj_attribute(name, float(widget.text()))
            )
            return line_edit
        else:
            label = QLabel(str(value))
            return label

    @QtCore.Slot(str, int)
    @QtCore.Slot(str, str)
    def update_obj_attribute(self, attribute_name, new_value):
        # Assuming obj is a QObject or a similar class with a signal attribute_changed
        print("update_obj_attribute", attribute_name, new_value, self.obj)
        setattr(self.obj, attribute_name, new_value)
        # self.obj_attribute_changed.emit(attribute_name, new_value)


def main():

    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    new_app = False
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv + ['-platform', 'windows:darkmode=2'])
        new_app = True

    # create graph controller.
    graph = NodeGraph()

    # use chdir() to set too
    os.chdir(os.path.dirname(__file__))

    # # set up context menu for the node graph.
    # # todo resources
    # # for now get locations from this module
    # from pathlib import Path
    # mod_path = Path(__file__).parent / "hotkeys/hotkeys.json"
    # print(mod_path )
    # graph.set_context_menu_from_file(mod_path )

    # set up context menu for the node graph.
    # todo resources
    # for now get locations from this module
    mod_path = os.path.dirname(__file__)
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

    def print_strings2(str1: str = 2, str2: str = None):
        import time

        # graph.widget.repaint() # todo move
        time.sleep(1)
        print(f"str1{str1}, str2{str2}")
        # graph.widget.repaint() # todo move

    pac_node_class = node_model_class_from_callable(print_strings2)
    node_class = ProcessNode.class_from_callable_class(pac_node_class)
    node_class2 = callable_node.create_callable_node_class(
        node_class, class_name="PrintStrings2", node_name="Print String Test2"
    )  # todo
    node_classes.append(node_class2)

    try:
        import pac2.blender
    except ImportError as e:
        print("Failed to import pac2.blender", e)
        pass

    for node_class in ProcessNode._node_classes:
        if issubclass(node_class, ProcessNode):
            name = node_class.__name__.split("_callable")[0]
            node_class2 = callable_node.create_callable_node_class(
                node_class, class_name=name, identifier="operators"
            )  # todo
        else:  # datanode
            name = node_class.__name__
            node_class2 = callable_node.create_data_node_class(node_class, class_name=name, identifier="data")

        node_classes.append(node_class2)

    # create data nodes
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

    # copy import
    from copy import copy

    for key, default_value in data_map.items():
        print("key", key, default_value)

        class _DataNode(Node):
            _default_value = default_value

            def __init__(self):
                super().__init__()
                self.data = copy(self._default_value)
                print("set data", self.data)

        _DataNode.__name__ = key  # + "Node"

        node_class2 = callable_node.create_callable_node_class(_DataNode, identifier="datanodes")  # todo
        node_classes.append(node_class2)

    print("node_classes", [x.__name__ for x in ProcessNode._node_classes])
    # print("node_class", node_class)

    # print("node_class2", type(pac_node), pac_node, dir(pac_node))
    # print(dir(pac_node()))
    # n = pac_node()
    # print("RUN")
    # n()
    # print("RUN")

    try:
        graph.register_nodes(node_classes)
    except:
        import traceback

        traceback.print_exc()

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

    main_widget = QtWidgets.QMainWindow()

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

        for n in Node._nodes.values():
            n.dumb_disconnect_all()
            n.state = NodeState.INIT

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
            if isinstance(node, CallableNodeBase) and isinstance(node._callable_node, ProcessNode):
                # get node connected to IN slot
                ports = node.inputs()["CALL"].connected_ports()
                if ports:
                    in_node = ports[0].node()
                    print("IN NODE", in_node)
                    in_node.start()
                else:
                    node.start()  # todo

                return  # only run 1 node, which should triggert the next nodes. # todo

    btn.clicked.connect(process_nodes)
    dock_btn = QtWidgets.QDockWidget()
    dock_btn.setWidget(btn)

    # create a dock widget for AttributeEditorWidget
    dock_attr_editor = QtWidgets.QDockWidget()
    widget_attr_editor = AttributeEditorWidget()
    dock_attr_editor.setWidget(widget_attr_editor)
    # ensure widget stretches to fill dock

    # def on_node_selection_changed(sel_nodes, unsel_nodes):
    #     print("sel_nodes", sel_nodes, unsel_nodes)
    #     view_node = sel_nodes[0] if len(sel_nodes) else None

    def node_created(view_node):
        load_ui_from_view_node(view_node)

    def node_selected(view_node):
        load_ui_from_view_node(view_node)

    def load_ui_from_view_node(view_node):
        if not view_node:
            widget_attr_editor.load_ui(None)
            return
        elif isinstance(view_node._callable_node, ProcessNode):
            widget_attr_editor.load_ui(view_node._callable_node.callable)
        elif isinstance(view_node._callable_node, Node):
            widget_attr_editor.load_ui(view_node._callable_node, attrs=["data"])

    graph.node_created.connect(node_created)
    graph.node_selected.connect(node_selected)

    main_widget.setCentralWidget(graph_widget)
    main_widget.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_tree)
    main_widget.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_btn)
    main_widget.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_attr_editor)
    main_widget.show()

    # app = QApplication(sys.argv + ['-platform', 'windows:darkmode=2'])
    # app.setStyle('Fusion')
    # app.setPalette(get_darkModePalette(app))

    # from qt_material import apply_stylesheet
    # apply_stylesheet(app, theme='dark_amber.xml')
    # import unreal_stylesheet
    # unreal_stylesheet.setup(app)

    try:
        import qdarktheme

        qdarktheme.setup_theme()
    except:
        pass

    if new_app:
        app.exec_()

    return main_widget


if __name__ == '__main__':
    main()
