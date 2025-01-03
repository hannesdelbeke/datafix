from PySide6 import QtCore, QtGui, QtWidgets  # pylint: disable=no-name-in-module
import site


site.addsitedir(r'D:\repos\pyblish-simple')
from pyblish_simple import view


class Ui_Form(view.Ui_Form):
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
    show()