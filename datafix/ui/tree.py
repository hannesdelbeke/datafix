try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QTreeView
    from PySide6.QtGui import QStandardItemModel, QStandardItem
except ImportError:
    from PySide2.QtWidgets import QApplication, QMainWindow, QTreeView
    from PySide2.QtGui import QStandardItemModel, QStandardItem

from datafix.core import Session  # Assuming this module exists


class NodeTreeView(QMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setWindowTitle("Parent Structure Tree")

        # Create the tree view
        self.tree_view = QTreeView(self)

        # Set up the model
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Node Name"])

        # Populate the model with the parent structure
        root_item = model.invisibleRootItem()
        root_node_item = QStandardItem("active_session")
        root_item.appendRow(root_node_item)

        # Recursively add nodes
        session = Session.active
        self.populate_tree(root_node_item, session)

        # Assign model to the tree view
        self.tree_view.setModel(model)
        self.tree_view.expandAll()  # Expand all nodes by default

        self.setCentralWidget(self.tree_view)

    def populate_tree(self, parent_item, node):
        """
        Recursively populate the tree with nodes and their children.
        """
        for child in node.children:
            child_item = QStandardItem(child.__class__.__name__)
            parent_item.appendRow(child_item)
            self.populate_tree(child_item, child)  # Recurse into children


if __name__ == "__main__":
    """
    Test code for the Qt tree widget, displaying the session as a collapsable node-graph
    
    Node Name
    active_session
    ├── CollectHelloWorld
    ├──── DataNode
    ├──── DataNode
    ├── ValidateHelloWorld
    ├──── ResultNode
    ├──── ResultNode
    """
    app = QApplication([])

    from tests.test_simple import setup_sample_pipeline
    setup_sample_pipeline()
    session = Session.active
    session.run()

    window = NodeTreeView()
    window.show()
    app.exec()
