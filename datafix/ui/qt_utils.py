from PySide6 import QtWidgets, QtGui


class States:
    INIT = 0
    SUCCESS = 1
    FAIL = 3
    WARNING = 4
    DISABLED = 5


def color_item(item: QtWidgets.QListWidgetItem, state=States.INIT, color_text=False, add_icon=1):
    """color a qlist widget item based on state

    color_text: if True, color the text of the item, if not rely on the color of the square
    add_icon: if True, adds an icon to the item text
    """
    if not item:
        raise ValueError("item is None")

    if state == States.INIT:
        color = 'white'
        icon = "🔲"  # white square
    elif state == States.FAIL:
        color = 'red'
        # icon = "🟥"  # red square
        icon = "❌"  # cross mark for failure
    elif state == States.WARNING:
        color = 'orange'
        # icon = "🟨"  # yellow square
        icon = "⚠️"  # warning sign
    elif state == States.SUCCESS:
        color = 'lime'
        # icon = "🟩"  # green square
        icon = "✅"  # checkmark for success
    elif state == States.DISABLED:
        color = 'gray'
        icon = '⬛'  # black square
    else:
        color = 'magenta'
        # icon = '🟪'
        icon = "❓"  # question mark for unknown state

    # set status icon
    if add_icon:
        if not item.text()[0].isalnum():  # check if first char is not already a square
            item_label = icon + item.text()[1:]  # replace first char with square
        else:
            item_label = icon + item.text()
        item.setText(item_label)

    # color the text
    if color_text:
        # text color will always work, but might clash with selection colors of stylesheets
        # icons do not clash with stylesheet colors
        item.setForeground(QtGui.QColor(color))

    if not add_icon and not color_text:
        # if we don't color the text, we can set the background color as a backup
        item.setBackground(QtGui.QColor(color))

if __name__ == "__main__":
    """Test code for the color_item function in a QListWidget"""
    import sys
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QListWidget()
    widget.addItem("fail")
    widget.addItem("success")
    widget.addItem("warning")
    widget.addItem("disabled")
    widget.addItem("init")
    widget.addItem("unknown")

    widget.addItem("fail")
    widget.addItem("success")
    widget.addItem("warning")
    widget.addItem("disabled")
    widget.addItem("init")
    widget.addItem("unknown")

    widget.show()

    color_item(widget.item(0), States.FAIL, color_text=False)
    color_item(widget.item(1), States.SUCCESS, color_text=False)
    color_item(widget.item(2), States.WARNING, color_text=False)
    color_item(widget.item(3), States.DISABLED, color_text=False)
    color_item(widget.item(4), States.INIT, color_text=False)
    color_item(widget.item(5), 99, color_text=False)

    color_item(widget.item(6), States.FAIL, color_text=True)
    color_item(widget.item(7), States.SUCCESS, color_text=True)
    color_item(widget.item(8), States.WARNING, color_text=True)
    color_item(widget.item(9), States.DISABLED, color_text=True)
    color_item(widget.item(10), States.INIT, color_text=True)
    color_item(widget.item(11), 99, color_text=True)

    sys.exit(app.exec_())