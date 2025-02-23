from PySide6 import QtCore, QtGui, QtWidgets  # pylint: disable=no-name-in-module

import datafix.node
import datafix.logic as datafix

from ui_demo import view, qt_utils


# hookup states
qt_utils.States.INIT = datafix.Node.NodeState.INIT
qt_utils.States.SUCCESS = datafix.Node.NodeState.SUCCEED
qt_utils.States.FAIL = datafix.Node.NodeState.FAIL
qt_utils.States.WARNING = datafix.Node.NodeState.WARNING


class Ui_Form(view.Ui_Form):
    run_on_startup = True

    def __init__(self, parent=None, *args, **kwargs):
        super(Ui_Form, self).__init__(parent=parent, *args, **kwargs)

        # connect plugin_selection_changed
        self.list_plugins.currentItemChanged.connect(self.plugin_selection_changed)

        if self.run_on_startup:
            self.clicked_check()

    def populate_ui(self):
        # run collectors, and add to list
        for plugin_class in datafix.active_session.nodes:
            name = plugin_class.__name__
            item = QtWidgets.QListWidgetItem(name)
            item.setData(QtCore.Qt.UserRole, plugin_class)
            self.list_plugins.addItem(name)

        self.color_plugin_items()


    def clicked_check(self):

        # run validation
        datafix.active_session.run()

        # color the list of results
        self.color_plugin_items()

        # select the first item
        self.list_plugins.setCurrentRow(0)

    def clicked_fix(self):
        # todo fix actions
        ...

    def plugin_selection_changed(self):
        if len(datafix.active_session.node_instances) == 0:
            # skip if not run yet
            return

        # get the selected plugin
        selected_item = self.list_plugins.currentItem()
        plugin_class = selected_item.data(QtCore.Qt.UserRole)
        current_index = self.list_plugins.currentRow()

        node = datafix.active_session.node_instances[current_index]

        # clear the list of results
        self.list_results.clear()

        # add the validators to the list
        for node in node.children:
            name = str(node.data)
            item = QtWidgets.QListWidgetItem(name)
            # item.setData(QtCore.Qt.UserRole, validator)

            node_state = node.state
            # if node.continue_on_fail:
            #     node_state = qt_utils.States.WARNING

            qt_utils.color_item(item, node_state)
            self.list_results.addItem(item)



    def color_plugin_items(self):
        for index, node in enumerate(datafix.active_session.nodes):
            item = self.list_plugins.item(index)

            if len(datafix.active_session.node_instances) == 0:
               # small hack to make it work when nodes arent instanced yet
                node_state = datafix.Node.NodeState.INIT
            else:
                node = datafix.active_session.node_instances[index]
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
    show()