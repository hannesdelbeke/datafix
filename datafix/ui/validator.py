from PySide6 import QtCore, QtWidgets, QtGui   # pylint: disable=no-name-in-module
import datafix.core
from datafix.ui import view, qt_utils

# hookup states
qt_utils.States.INIT = datafix.core.NodeState.INIT
qt_utils.States.SUCCESS = datafix.core.NodeState.SUCCEED
qt_utils.States.FAIL = datafix.core.NodeState.FAIL
qt_utils.States.WARNING = datafix.core.NodeState.WARNING


class Ui_Form(view.Ui_Form):
    run_on_startup = False

    def __init__(self, parent=None, *args, **kwargs):
        super(Ui_Form, self).__init__(parent=parent, *args, **kwargs)
        self.session = None
        self.load_session()

        self.list_session_nodes.currentItemChanged.connect(self.session_node_selection_changed)

        # Add context menu for session nodes list
        self.list_session_nodes.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_session_nodes.customContextMenuRequested.connect(self.show_session_context_menu)

        # Add context menu for child nodes list
        self.list_child_nodes.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_child_nodes.customContextMenuRequested.connect(self.show_child_context_menu)

        if self.run_on_startup:
            self.clicked_check()

        # init UI
        self.session_node_selection_changed()

    def load_session(self, session=None):
        # clear any existing nodes
        self.list_session_nodes.clear()
        self.list_child_nodes.clear()
        self.session = session or datafix.core.active_session
        self.load_session_nodes_in_ui()

    def load_session_nodes_in_ui(self):
        # run collectors, and add to list
        for node in self.session.children:
            name = node.name
            item = QtWidgets.QListWidgetItem(name)
            item.setData(QtCore.Qt.UserRole, node)
            item.objectName = node.state.name
            self.list_session_nodes.addItem(item)
        self.color_items_in_list_session_nodes()

    def clicked_check(self):
        # run validation
        self.session.run()
        self.color_items_in_list_session_nodes()  # color the list of results
        # self.list_session_nodes.setCurrentRow(0)  # select the first item
        self.session_node_selection_changed()  # update UI

    def clicked_fix(self):
        # todo fix actions

        # we run fix actions on any node.
        # e.g. fix on a resultnodes (most common)
        ...

    def show_session_context_menu(self, pos):
        self.show_context_menu(pos, self.list_session_nodes)

    def show_child_context_menu(self, pos):
        self.show_context_menu(pos, self.list_child_nodes)

    def show_context_menu(self, pos, list_widget):
        # Get the right-clicked item
        item = list_widget.itemAt(pos)
        if not item:
            return

        node = item.data(QtCore.Qt.UserRole)

        # Create the context menu
        menu = QtWidgets.QMenu(self)
        for action in node.actions:
            menu_action = QtGui.QAction(action.name, self)
            menu_action.triggered.connect(lambda checked=None, a=action: a.run())
            menu.addAction(menu_action)

        # Show the menu at the cursor position
        menu.exec(list_widget.viewport().mapToGlobal(pos))

    def session_node_selection_changed(self):
        if len(self.session.children) == 0:
            return

        selected_item = self.list_session_nodes.currentItem()
        if not selected_item:
            return
        session_node = selected_item.data(QtCore.Qt.UserRole)

        if not session_node:
            print("no node selected, cancel node_selection_changed")
            return

        self.list_child_nodes.clear()
        for child_node in session_node.children:
            name = child_node.name
            item = QtWidgets.QListWidgetItem(name)
            qt_utils.color_item(item, child_node.state)
            item.setData(QtCore.Qt.UserRole, child_node)
            self.list_child_nodes.addItem(item)

    def color_items_in_list_session_nodes(self):
        for index, node in enumerate(self.session.children):
            item = self.list_session_nodes.item(index)

            if len(self.session.children) == 0:
               # small hack to make it work when nodes aren't instanced yet
                node_state = datafix.core.NodeState.INIT
            else:
                node = self.session.children[index]
                node_state = node.state
            qt_utils.color_item(item, node_state)


def show(parent=None, session=None):
    app = QtWidgets.QApplication.instance()

    new_app_created = False
    if not app:
        app = QtWidgets.QApplication([])
        new_app_created = True

    window = Ui_Form(parent=parent)
    window.load_session(session)
    window.show()

    if new_app_created:
        app.exec()

    return window


if __name__ == '__main__':
    """ test code to test UI with collectors, validators, and actions """
    from tests.test_simple import setup_sample_pipeline
    setup_sample_pipeline()
    show()
