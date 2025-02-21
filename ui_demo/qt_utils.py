from PySide6 import QtWidgets, QtGui


class States:
    INIT = 0
    SUCCESS = 1
    FAIL = 3
    WARNING = 4
    DISABLED = 5


def color_item(item: QtWidgets.QListWidgetItem, state=States.INIT):
    """color a qlist widget item based on state"""
    if not item:
        raise ValueError("item is None")

    if state == States.INIT:
        color = 'white'
        square = "🔲"
    elif state == States.FAIL:
        color = 'red'
        square = "🟥"
    elif state == States.WARNING:
        color = 'orange'
        square = "🟨"
    elif state == States.SUCCESS:
        color = 'lime'
        square = "🟩"
    elif state == States.DISABLED:
        color = 'gray'
        square = '⬛'
    else:
        color = 'magenta'
        square = '🟪'

    # set status square
    if not item.text()[0].isalnum():  # check if first char is not already a square
        item_label = square + item.text()[1:]  # replace first char with square
    else:
        item_label = square + item.text()
    item.setText(item_label)

    print("color", color)
    print("square", square)
    # set color
    item.setForeground(QtGui.QColor(color))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QListWidget()
    widget.addItem("fail")
    widget.addItem("success")
    widget.addItem("warning")
    widget.addItem("disabled")
    widget.addItem("init")
    widget.addItem("unknown")
    widget.show()

    color_item(widget.item(0), States.FAIL)
    color_item(widget.item(1), States.SUCCESS)
    color_item(widget.item(2), States.WARNING)
    color_item(widget.item(3), States.DISABLED)
    color_item(widget.item(4), States.INIT)
    color_item(widget.item(5), 99)

    sys.exit(app.exec_())