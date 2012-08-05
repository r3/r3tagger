import sys

from PySide.QtCore import Qt
from PySide.QtGui import (QMainWindow, QFileSystemModel, QHBoxLayout, QAction,
                          QTreeView, QApplication, QWidget, QVBoxLayout,
                          QAbstractItemView, QDockWidget, QLabel, QLineEdit,
                          QPushButton, QTableView, QKeySequence, QIcon,
                          QStandardItemModel, QStandardItem,
                          QItemSelectionModel)

from r3tagger import Controller


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Models
        self.fsModel = QFileSystemModel()
        fsRoot = self.fsModel.setRootPath('/home/ryan/Programming/Python/projects/r3tagger/r3tagger')

        self.listModel = AlbumCollectionModel()

        # Views
        self.filesystem = QTreeView()
        self.filesystem.setModel(self.fsModel)
        self.filesystem.setRootIndex(fsRoot)
        self.filesystem.doubleClicked.connect(self.updateListing)

        self.listing = QTableView()
        self.listing.setModel(self.listModel)
        self.listing.setSelectionMode(QAbstractItemView.MultiSelection)
        self.listing.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.listing.verticalHeader().hide()
        self.listing.clicked.connect(self.updateEditing)

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
            line = QLineEdit()
            horizLayout.addWidget(line)
            setattr(self, field + 'Field', line)
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

        # Zero collection:
        self.listModel.clearAlbums()

        # Add new albums
        for album in Controller.build_albums(path, recursive=True):
            self.listModel.addAlbum(album)

    def updateEditing(self):

        index = form.listModel.index(3, 0)
        form.listing.setCurrentIndex(index)
        #albums = self.selectedAlbums()
        # Get selection from model
        #print(albums)

    def selectedAlbums(self):
        selected_rows = {x.row() for x in self.listing.selectedIndexes()}
        return [self.listModel.albums[x] for x in selected_rows]

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


class AlbumCollectionModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(AlbumCollectionModel, self).__init__(parent)

        self.albums = []
        self.columns = ("title", "artist", "album", "track_number")

    def addAlbum(self, album):
        self.albums.append(album)

        album_row = self._build_row(album)
        album_row[0].isAlbum = True
        self.appendRow(album_row)

        for track in album:
            track_row = self._build_row(track)
            self.appendRow(track_row)

    def _build_row(self, model):
        row = []

        for column in self.columns:
            try:
                field = getattr(model, column)
                row.append(QStandardItem(field))

            except AttributeError:
                row.append(QStandardItem(''))

        return row

    def clearAlbums(self):
        self.albums = []
        self.clear()


class QAlbum():
    def __init__(self, album):
        self.album = album

        self.tracks = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("r3")
    app.setOrganizationDomain("github.com/r3")
    app.setApplicationName("r3tagger")

    form = MainWindow()
    form.show()

    sys.exit(app.exec_())
