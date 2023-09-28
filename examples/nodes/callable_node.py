#!/usr/bin/python
import logging

from Qt import QtCore, QtGui
import pac2.node
from NodeGraphQt import BaseNode


def draw_triangle_port(painter, rect, info):
    """
    Custom paint function for drawing a Triangle shaped port.

    Args:
        painter (QtGui.QPainter): painter object.
        rect (QtCore.QRectF): port rect used to describe parameters
                              needed to draw.
        info (dict): information describing the ports current state.
            {
                'port_type': 'in',
                'color': (0, 0, 0),
                'border_color': (255, 255, 255),
                'multi_connection': False,
                'connected': False,
                'hovered': False,
            }
    """
    painter.save()

    size = int(rect.height() / 2)
    triangle = QtGui.QPolygonF()
    triangle.append(QtCore.QPointF(-size, size))
    triangle.append(QtCore.QPointF(-size, -size))
    triangle.append(QtCore.QPointF(size / 2, 0))

    transform = QtGui.QTransform()
    transform.translate(rect.center().x(), rect.center().y())
    port_poly = transform.map(triangle)

    # mouse over port color.
    if info['hovered']:
        color = QtGui.QColor(14, 45, 59)
        border_color = QtGui.QColor(136, 255, 35)
    # port connected color.
    elif info['connected']:
        color = QtGui.QColor(195, 60, 60)
        border_color = QtGui.QColor(200, 130, 70)
    # default port color
    else:
        color = QtGui.QColor(*info['color'])
        border_color = QtGui.QColor(*info['border_color'])

    pen = QtGui.QPen(border_color, 1.8)
    pen.setJoinStyle(QtCore.Qt.MiterJoin)

    painter.setPen(pen)
    painter.setBrush(color)
    painter.drawPolygon(port_poly)

    painter.restore()


class CallableNodeBase(BaseNode):
    """Node View for a callable Node"""

    # set a unique node identifier.
    __identifier__ = 'nodes.callable'

    # set the initial default node name.
    NODE_NAME = 'process node'

    def __init__(self, callable_node_class):
        super().__init__()

        # create input and output port.
        self.add_input(
            'CALL', painter_func=draw_triangle_port, multi_input=False, color=(255, 255, 255)
        )  #  color=(200, 10, 0),
        self.add_output('OUT', painter_func=draw_triangle_port, color=(255, 255, 255))
        self.add_output('output')
        # self._callable_node_class = callable_node_class
        self._callable_node: "pac2.ProcessNode" = callable_node_class()
        self._callable_node.callbacks_state_changed.append(self.on_state_changed)

    def set_callable_node(self, callable_node):
        self._callable_node = callable_node
        self._callable_node.callbacks_state_changed.append(self.on_state_changed)

    def run(self):
        self._callable_node()  # run the node, the node fails, warns, succeeds.

    def start(self):
        self._callable_node.start()

    def on_state_changed(self, state):
        color = (255, 255, 255)  # white init
        if state == pac2.node.NodeState.FAIL:
            if self._callable_node.continue_on_error:
                color = (255, 255, 0)  # yellow warning
            else:
                color = (255, 0, 0)  # red error
        elif state == pac2.node.NodeState.SUCCEED:
            color = (0, 255, 0)  # green success
        elif state == pac2.node.NodeState.INIT:
            color = (255, 255, 255)  # white init
        elif state == pac2.node.NodeState.INIT:
            # pink
            color = (255, 255, 255)  # white init
        else:
            color = (255, 0, 255)  # pink
        # self.set_color(255, 255, 0)  # yellow warning
        self.view.border_color = color
        self.view.update()
        self.graph.widget.repaint()


def create_callable_node_class(callable_node_class, class_name=None, identifier=None, node_name=None):
    class_name = class_name or callable_node_class.__name__ + "Node"  # todo split name

    class CallableNode(CallableNodeBase):
        def __init__(self):
            # print("INIT callable_node_class", callable_node_class)
            super().__init__(callable_node_class)

            # print("self._callable_node", self._callable_node.callable)
            # print(type(self._callable_node.callable))
            # get input slots from callable_node_class
            try:
                for attr_name in self._callable_node.callable._default_map_.keys():
                    self.add_input(attr_name)  # , color=(255, 255, 255))
            except AttributeError:
                logging.warning(f"callable_node_class '{class_name}' has no callable attribute")

    if identifier:
        CallableNode.__identifier__ = identifier

    CallableNode.__name__ = class_name
    CallableNode.NODE_NAME = node_name or class_name

    return CallableNode
