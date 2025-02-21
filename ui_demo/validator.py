from PySide6 import QtCore, QtGui, QtWidgets  # pylint: disable=no-name-in-module
import site
import datafix.logic as datafix
import logging

from ui_demo import view, qt_utils


# hookup states
qt_utils.States.INIT = datafix.NodeState.INIT
qt_utils.States.SUCCESS = datafix.NodeState.SUCCEED
qt_utils.States.FAIL = datafix.NodeState.FAIL
qt_utils.States.WARNING = datafix.NodeState.WARNING



class Ui_Form(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Ui_Form, self).__init__(parent)
        self.create_ui()
        self.populate_ui()

    def create_ui(self):
        # self.set_dark_theme()

        # self.dropdown_families = QtWidgets.QComboBox()
        # self.dropdown_validators = QtWidgets.QComboBox()
        self.list_plugins = QtWidgets.QListWidget()
        self.list_results = QtWidgets.QListWidget()
        self.button_check = QtWidgets.QPushButton('Check All')
        self.button_fix = QtWidgets.QPushButton('Fix All')

        # get list of collector plugins we just ran
        # self.collectors = list(p for p in self.plugins if pyblish.lib.inrange(
        #     number=p.order,
        #     base=pyblish.api.CollectorOrder))

        vlayout_instances = QtWidgets.QVBoxLayout()
        # vlayout_instances.addWidget(self.dropdown_families)
        vlayout_instances.addWidget(self.list_plugins)
        vlayout_instances.addWidget(self.button_check)

        vlayout_validators = QtWidgets.QVBoxLayout()
        # vlayout_validators.addWidget(self.dropdown_validators)
        vlayout_validators.addWidget(self.list_results)
        vlayout_validators.addWidget(self.button_fix)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addLayout(vlayout_instances)
        hlayout.addLayout(vlayout_validators)
        self.setLayout(hlayout)

        # connect
        self.button_check.clicked.connect(self.clicked_check)
        # self.button_fix.clicked.connect(self.clicked_fix)


class Ui_Form(view.Ui_Form):

    def __init__(self, parent=None, *args, **kwargs):
        super(Ui_Form, self).__init__(parent=parent, *args, **kwargs)

        # connect plugin_selection_changed
        self.list_plugins.currentItemChanged.connect(self.plugin_selection_changed)

    def populate_ui(self):
        # run collectors, and add to list
        for plugin_class in datafix.active_session.nodes:
            name = plugin_class.__name__
            item = QtWidgets.QListWidgetItem(name)
            item.setData(QtCore.Qt.UserRole, plugin_class)
            self.list_plugins.addItem(name)

        self.color_plugin_items()


    def clicked_check(self):

        print("check")
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
        print("plugin_selection_changed")
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
            print(node.state, "state")



    def color_plugin_items(self):
        for index, node in enumerate(datafix.active_session.nodes):
            item = self.list_plugins.item(index)

            if len(datafix.active_session.node_instances) == 0:
               # small hack to make it work when nodes arent instanced yet
                node_state = datafix.NodeState.INIT
            else:
                node = datafix.active_session.node_instances[index]
                print("item", item)
                print("node", node)
                # plugin_class = item.data(QtCore.Qt.UserRole)
                print(node.state)
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