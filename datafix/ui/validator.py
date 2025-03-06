from PySide6 import QtCore, QtWidgets  # pylint: disable=no-name-in-module

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
        self.load_session_nodes_in_ui()

        self.list_session_nodes.currentItemChanged.connect(self.session_node_selection_changed)

        if self.run_on_startup:
            self.clicked_check()


    def load_session_nodes_in_ui(self):
        # run collectors, and add to list
        for node in datafix.core.active_session.children:
            print(node)
            name = node.name
            item = QtWidgets.QListWidgetItem(name)
            item.setData(QtCore.Qt.UserRole, node)
            # set item setObjectName
            item.objectName = node.state.name
            self.list_session_nodes.addItem(item)

        self.color_items_in_list_session_nodes()


    def clicked_check(self):

        # run validation
        datafix.core.active_session.run()


        self.color_items_in_list_session_nodes()  # color the list of results
        self.list_session_nodes.setCurrentRow(0)  # select the first item

    def clicked_fix(self):
        # todo fix actions

        # we run fix actions on any node.
        # e.g. fix on a resultnodes (most common)

        ...

    def session_node_selection_changed(self):
        if len(datafix.core.active_session.children) == 0:
            # skip if not run yet
            return

        # get the selected node
        selected_item = self.list_session_nodes.currentItem()
        session_node = selected_item.data(QtCore.Qt.UserRole)

        if not session_node:
            print("no node selected, cancel node_selection_changed")
            return
        # current_index = self.list_session_nodes.currentRow()
        # node = datafix.core.active_session.children[current_index]

        # clear the list of results
        self.list_child_nodes.clear()

        # add the validators to the list
        for child_node in session_node.children:
            name = str(child_node.data)
            item = QtWidgets.QListWidgetItem(name)
            # item.setData(QtCore.Qt.UserRole, validator)

            node_state = child_node.state
            # if node.continue_on_fail:
            #     node_state = qt_utils.States.WARNING

            qt_utils.color_item(item, node_state)
            self.list_child_nodes.addItem(item)

    def color_items_in_list_session_nodes(self):
        for index, node in enumerate(datafix.core.active_session.children):
            item = self.list_session_nodes.item(index)

            if len(datafix.core.active_session.children) == 0:
               # small hack to make it work when nodes arent instanced yet
                node_state = datafix.core.NodeState.INIT
            else:
                node = datafix.core.active_session.children[index]
                node_state = node.state
            qt_utils.color_item(item, node_state)


def show(parent=None):
    app = QtWidgets.QApplication.instance()

    new_app_created = False
    if not app:
        app = QtWidgets.QApplication([])
        new_app_created = True

    window = Ui_Form(parent=parent)
    window.show()

    if new_app_created:
        app.exec()

    return window


if __name__ == '__main__':
    from tests.test_simple import setup_sample_pipeline
    setup_sample_pipeline()
    show()