import sys

from PySide.QtCore import Qt
from PySide.QtGui import (QMainWindow, QFileSystemModel, QHBoxLayout,
                          QTreeView, QApplication, QWidget, QVBoxLayout,
                          QAbstractItemView, QDockWidget, QLabel, QLineEdit,
                          QPushButton)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.fsModel = QFileSystemModel()
        fsRoot = self.fsModel.setRootPath('/')

        self.listModel = QFileSystemModel()
        lsRoot = self.listModel.setRootPath('/')

        self.filesystem = QTreeView()
        self.filesystem.setModel(self.fsModel)
        self.filesystem.setRootIndex(fsRoot)
        self.filesystem.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.filesystem.clicked.connect(self.updateListing)

        dockView = QDockWidget("Navigate", self)
        dockView.setObjectName("dockView")
        dockView.setAllowedAreas(Qt.LeftDockWidgetArea)
        dockView.setWidget(self.filesystem)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockView)

        self.listing = QTreeView()
        self.listing.setModel(self.listModel)
        self.listing.setRootIndex(lsRoot)
        self.listing.setSelectionMode(QAbstractItemView.MultiSelection)

        self.taggingGroup = QVBoxLayout()
        for field in ("artist", "album", "date", "track", "number"):
            horizLayout = QHBoxLayout()
            horizLayout.addWidget(QLabel(field))
            horizLayout.addWidget(QLineEdit())
            self.taggingGroup.addLayout(horizLayout)

        self.buttonGroup = QHBoxLayout()
        self.buttonGroup.addWidget(QPushButton("Confirm"))
        self.buttonGroup.addWidget(QPushButton("Cancel"))
        self.buttonGroup.addStretch()

        self.taggingGroup.addStretch()
        self.taggingGroup.addLayout(self.buttonGroup)

        layout = QHBoxLayout()
        layout.addWidget(self.listing)
        layout.addLayout(self.taggingGroup)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

    def updateListing(self, index):
        path = self.fsModel.fileInfo(index).absoluteFilePath()
        root = self.listModel.setRootPath(path)
        self.listing.setRootIndex(root)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("r3")
    app.setOrganizationDomain("github.com/r3")
    app.setApplicationName("r3tagger")

    form = MainWindow()
    form.show()

    sys.exit(app.exec_())
