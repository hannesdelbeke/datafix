from Qt import QtWidgets
from NodeGraphQt import NodeGraph, BaseNode
from NodeGraphQt import NodeGraph, NodesTreeWidget


# create a node class object inherited from BaseNode.
class FooNode(BaseNode):

    # unique node identifier domain.
    __identifier__ = 'io.github.jchanvfx'

    # initial default node name.
    NODE_NAME = 'Foo Node'

    def __init__(self):
        super(FooNode, self).__init__()

        # create an input port.
        self.add_input('in', color=(180, 80, 0))

        # create an output port.
        self.add_output('out')


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    # create node graph controller.
    graph = NodeGraph()

    nodes_tree = NodesTreeWidget(parent=None, node_graph=graph)
    # nodes_tree.show()

    # register the FooNode node class.
    graph.register_node(FooNode)

    # show the node graph widget.
    graph_widget = graph.widget
    # graph_widget.show()

    # wrap in dockable widget
    from Qt import QtWidgets

    # widget = QtWidgets.QDockWidget()
    # widget.setWidget(graph_widget)
    # widget.show()

    # create a widget
    widget = QtWidgets.QMainWindow()
    widget.setCentralWidget(graph_widget)
    # layout = QtWidgets.QHBoxLayout(widget)
    # layout.addWidget(graph_widget)
    # layout.addWidget(nodes_tree)
    widget.show()

    widget2 = QtWidgets.QDockWidget(parent=widget)
    widget2.setWidget(nodes_tree)
    widget2.show()
    from Qt import QtCore

    widget.addDockWidget(QtCore.Qt.LeftDockWidgetArea, widget2)
    # start widget docked to the right
    # widget2.setFloating(False)
    # widget2.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
    # widget2.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
    # show menu

    menu_bar = widget.menuBar()
    file_menu = menu_bar.addMenu('&File')

    # create two nodes.
    node_a = graph.create_node('io.github.jchanvfx.FooNode', name='node A')
    node_b = graph.create_node('io.github.jchanvfx.FooNode', name='node B', pos=(300, 50))

    # connect node_a to node_b
    node_a.set_output(0, node_b.input(0))

    nodes_tree.update()
    app.exec_()
