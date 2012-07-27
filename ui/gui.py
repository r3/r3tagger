import sys
import os

from PySide.QtCore import Qt
from PySide.QtGui import (QMainWindow, QFileSystemModel, QHBoxLayout, QAction,
                          QTreeView, QApplication, QWidget, QVBoxLayout,
                          QAbstractItemView, QDockWidget, QLabel, QLineEdit,
                          QPushButton, QTableView, QKeySequence, QIcon)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Models
        self.fsModel = QFileSystemModel()
        fsRoot = self.fsModel.setRootPath(os.path.curdir)

        self.listModel = QFileSystemModel()
        lsRoot = self.listModel.setRootPath(os.path.curdir)

        # Views
        self.filesystem = QTreeView()
        self.filesystem.setModel(self.fsModel)
        self.filesystem.setRootIndex(fsRoot)
        self.filesystem.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.filesystem.clicked.connect(self.updateListing)

        self.listing = QTableView()
        self.listing.setModel(self.listModel)
        self.listing.setRootIndex(lsRoot)
        self.listing.setSelectionMode(QAbstractItemView.MultiSelection)

        # Statusbar
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage("Ready", 5000)

        # Docks
        dockView = QDockWidget("Navigate", self)
        dockView.setObjectName("dockView")
        dockView.setAllowedAreas(Qt.LeftDockWidgetArea)
        dockView.setWidget(self.filesystem)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockView)

        # Tag Editing Group
        self.taggingGroup = QVBoxLayout()
        for field in ("artist", "album", "date", "track", "number"):
            horizLayout = QHBoxLayout()
            horizLayout.addWidget(QLabel(field))
            horizLayout.addWidget(QLineEdit())
            self.taggingGroup.addLayout(horizLayout)

        # Confirm / Cancel Button Group
        self.buttonGroup = QHBoxLayout()
        self.buttonGroup.addWidget(QPushButton("Confirm"))
        self.buttonGroup.addWidget(QPushButton("Cancel"))
        self.buttonGroup.addStretch()

        # Layout
        self.taggingGroup.addStretch()
        self.taggingGroup.addLayout(self.buttonGroup)
        layout = QHBoxLayout()
        layout.addWidget(self.listing)
        layout.addLayout(self.taggingGroup)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        # Actions
        fileOpenAction = self.createAction("&Open", self.fileOpen,
                QKeySequence.Open, 'fileopen', "Open location")
        fileSaveAction = self.createAction("&Confirm", self.fileSave,
                QKeySequence.Save, 'filesave', "Confirm changes")
        fileQuitAction = self.createAction("&Quit", self.fileQuit,
                QKeySequence.Quit, 'filequit', "Quit program")
        editRecognizeAction = self.createAction("&Recognize",
                self.editRecognize, QKeySequence(Qt.CTRL + Qt.Key_R),
                'editrecognize', "Recognize music")
        editReorganizeAction = self.createAction("Reorganize",
                self.editReorganize, QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_R),
                'editreorganize', "Reorganize music")
        editSettingsAction = self.createAction("Settings", self.editSettings,
                QKeySequence.Preferences, 'editsettings', "Edit settings")
        helpDocsAction = self.createAction("Documentation", self.helpDocs,
                QKeySequence.HelpContents, 'helpdocs', "Documentation")
        helpAboutAction = self.createAction("About", self.helpAbout,
                QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_F1),
                'helpabout', "About")

        # Menus
        fileMenu = self.menuBar().addMenu("&File")
        self.addActions(fileMenu, (fileOpenAction, fileSaveAction, fileQuitAction))

        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (editReorganizeAction, editRecognizeAction, \
                                   editSettingsAction))

        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, (helpDocsAction, helpAboutAction))

        # Toolbars
        fileToolbar = self.addToolBar("FileToolbar")
        fileToolbar.setObjectName("fileToolbar")
        self.addActions(fileToolbar, (fileOpenAction, fileSaveAction))

        editToolbar = self.addToolBar("EditToolbar")
        editToolbar.setObjectName("editToolbar")
        self.addActions(editToolbar, (editRecognizeAction,
                                      editReorganizeAction))

    def updateListing(self, index):
        path = self.fsModel.fileInfo(index).absoluteFilePath()
        root = self.listModel.setRootPath(path)
        self.listing.setRootIndex(root)

    def fileOpen(self):
        pass

    def fileSave(self):
        pass

    def fileQuit(self):
        pass

    def editRecognize(self):
        pass

    def editReorganize(self):
        pass

    def editSettings(self):
        pass

    def helpDocs(self):
        pass

    def helpAbout(self):
        pass

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/{0}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            getattr(action, signal).connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("r3")
    app.setOrganizationDomain("github.com/r3")
    app.setApplicationName("r3tagger")

    form = MainWindow()
    form.show()

    sys.exit(app.exec_())
