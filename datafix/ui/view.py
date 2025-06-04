from PySide6 import QtCore, QtGui, QtWidgets  # pylint: disable=no-name-in-module


class Ui_Form(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Ui_Form, self).__init__(parent)
        self.create_ui()

    def create_ui(self):
        # self.set_dark_theme()

        # self.dropdown_families = QtWidgets.QComboBox()
        # self.dropdown_validators = QtWidgets.QComboBox()
        self.list_session_nodes = QtWidgets.QListWidget()
        self.list_child_nodes = QtWidgets.QListWidget()
        self.button_check = QtWidgets.QPushButton('Check All')
        self.button_fix = QtWidgets.QPushButton('Fix All')

        # get list of collector plugins we just ran
        # self.collectors = list(p for p in self.plugins if pyblish.lib.inrange(
        #     number=p.order,
        #     base=pyblish.api.CollectorOrder))

        vlayout_instances = QtWidgets.QVBoxLayout()
        # vlayout_instances.addWidget(self.dropdown_families)
        vlayout_instances.addWidget(self.list_session_nodes)
        vlayout_instances.addWidget(self.button_check)

        vlayout_validators = QtWidgets.QVBoxLayout()
        # vlayout_validators.addWidget(self.dropdown_validators)
        vlayout_validators.addWidget(self.list_child_nodes)
        vlayout_validators.addWidget(self.button_fix)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addLayout(vlayout_instances)
        hlayout.addLayout(vlayout_validators)
        self.setLayout(hlayout)

        # connect
        self.button_check.clicked.connect(self.clicked_check)
        # self.button_fix.clicked.connect(self.clicked_fix)


        # disable fix
        self.button_fix.setEnabled(False)

    # todo use action.on to filter when to show. ex. "failedOrWarning"

    def clicked_check(self):
        ...

    def clicked_fix(self):
        ...


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
    """empty UI test code, use datafix.ui.validator.show() instead to test the populated UI"""
    window = show()
