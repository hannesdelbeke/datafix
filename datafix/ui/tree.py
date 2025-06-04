from PySide6.QtWidgets import QApplication, QMainWindow, QTreeView
from PySide6.QtGui import QStandardItemModel, QStandardItem
from datafix.core import active_session  # Assuming this module exists

class NodeTreeView(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.populate_tree(root_node_item, active_session)

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
    active_session.run()

    window = NodeTreeView()
    window.show()
    app.exec()
