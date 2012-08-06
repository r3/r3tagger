import sys
from UserList import UserList

from PySide.QtCore import Qt
from PySide.QtGui import (QMainWindow, QFileSystemModel, QHBoxLayout, QAction,
                          QTreeView, QApplication, QWidget, QVBoxLayout,
                          QAbstractItemView, QDockWidget, QLabel, QLineEdit,
                          QPushButton, QTableView, QKeySequence, QIcon,
                          QStandardItemModel, QStandardItem,
                          QItemSelectionModel)

from r3tagger import Controller
from r3tagger.model.Album import Album


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
        self.mainLayout = QVBoxLayout()
        self.taggingGroup = QHBoxLayout()
        labels = QVBoxLayout()
        edits = QVBoxLayout()

        self.fieldArtist = QLabel("Artist:")
        labels.addWidget(self.fieldArtist)
        self.lineArtist = QLineEdit()
        edits.addWidget(self.lineArtist)

        self.fieldAlbum = QLabel("Album:")
        labels.addWidget(self.fieldAlbum)
        self.lineAlbum = QLineEdit()
        edits.addWidget(self.lineAlbum)

        self.fieldTitle = QLabel("Title:")
        labels.addWidget(self.fieldTitle)
        self.lineTitle = QLineEdit()
        edits.addWidget(self.lineTitle)

        self.fieldTrack = QLabel("Track:")
        labels.addWidget(self.fieldTrack)
        self.lineTrack = QLineEdit()
        edits.addWidget(self.lineTrack)

        self.fieldDate = QLabel("Date:")
        labels.addWidget(self.fieldDate)
        self.lineDate = QLineEdit()
        edits.addWidget(self.lineDate)

        self.fieldGenre = QLabel("Genre:")
        labels.addWidget(self.fieldGenre)
        self.lineGenre = QLineEdit()
        edits.addWidget(self.lineGenre)

        self.taggingGroup.addLayout(labels)
        self.taggingGroup.addLayout(edits)

        # Confirm / Cancel Button Group
        self.buttonGroup = QHBoxLayout()
        self.buttonGroup.addWidget(QPushButton("Confirm"))
        self.buttonGroup.addWidget(QPushButton("Cancel"))
        self.buttonGroup.addStretch()

        # Layout
        self.mainLayout.addLayout(self.taggingGroup)
        self.mainLayout.addStretch()
        self.mainLayout.addLayout(self.buttonGroup)
        layout = QHBoxLayout()
        layout.addWidget(self.listing)
        layout.addLayout(self.mainLayout)
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

    def correctListingSelection(self, index):
        def isSelected(index):
            return index in self.listing.selectedIndexes()

        def siblingsSelected(row):
            return all([isSelected(sibling.index) for sibling in row.siblings])

        def isAlbum(row):
            return row.parent is None

        def childrenSelected(row):
            return siblingsSelected(row.children[0])

        clicked_row = index.row()
        row = self.listModel.lookupRow(clicked_row)
        model = self.listing.selectionModel()

        if isAlbum(row):
            if isSelected(index):
                select_policy = QItemSelectionModel.Select
            elif childrenSelected(row):
                select_policy = QItemSelectionModel.Deselect
            else:
                select_policy = None

            if select_policy:
                for child in row.children:
                    for item in child:
                        model.setCurrentIndex(item.index(), select_policy)

        elif isSelected(index):
            if siblingsSelected(row) and not isSelected(row.parent):
                for item in row.parent:
                    model.setCurrentIndex(item.index(),
                            QItemSelectionModel.Select)

        else:
            for item in row.parent:
                model.setCurrentIndex(item.index(),
                        QItemSelectionModel.Deselect)

    def selectedRows(self):
        return {x.row() for x in self.listing.selectedIndexes()}

    def selectedAlbums(self):
        def isAlbum(row_number):
            return self.listModel.lookupRow(row_number).parent is None

        unwrap = self.listModel.lookupRowWrapped
        return [unwrap(x) for x in self.selectedRows() if isAlbum(x)]

    def selectedSingles(self):
        def isTrack(row_number):
            return self.listModel.lookupRow(row_number).parent is not None

        def parentNotSelected(row_number):
            parent_index = self.listModel.lookupRow(row_number).parent.index
            return parent_index not in self.listing.selectedIndexes()

        unwrap = self.listModel.lookupRowWrapped
        res = [unwrap(x) for x in self.selectedRows() if isTrack(x)
                and parentNotSelected(x)]
        return res

    def updateEditing(self, index):
        self.correctListingSelection(index)

        tags_to_attribs = {'artist': self.lineArtist,
                           'album': self.lineAlbum,
                           'title': self.lineTitle,
                           'tracknumber': self.lineTrack,
                           'date': self.lineDate,
                           'genre': self.lineGenre}

        singles = [Album({'tracks':[x]}) for x in self.selectedSingles()]
        selected = self.selectedAlbums() + singles
        tags = Controller.find_shared_tags(*selected) if selected else {}

        for tag, edit in tags_to_attribs.items():
            edit.setText(tags.get(tag, ''))

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


class TableRow(UserList):
    def __init__(self, contents, wrapped=None, parent=None):
        self.data = []
        self.data.extend(contents)
        self.wrapped = wrapped
        self.parent = parent
        self.children = []

    def __str__(self):
        return str(self.wrapped)

    def addChild(self, child):
        self.children.append(child)

    @property
    def index(self):
        return self[0].index()

    @property
    def siblings(self):
        if self.parent:
            return self.parent.children
        else:
            return None


class AlbumCollectionModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(AlbumCollectionModel, self).__init__(parent)

        self._rows = 0
        self.albums = {}
        self.columns = ("title", "artist", "album", "track_number")

    def addAlbum(self, album):
        album_row = TableRow(self._build_row(album), album)
        self.albums[self._rows] = album_row
        self.appendRow(album_row)

        for track in album:
            track_row = TableRow(self._build_row(track), track, album_row)
            album_row.addChild(track_row)
            self.albums[self._rows] = track_row
            self.appendRow(track_row)

    def appendRow(self, row):
        super(AlbumCollectionModel, self).appendRow(row)
        self._rows += 1

    def _build_row(self, model):
        row = []

        for column in self.columns:
            try:
                field = getattr(model, column)
                row.append(QStandardItem(field))

            except AttributeError:
                row.append(QStandardItem('_'))

        return row

    def clearAlbums(self):
        self.albums = {}
        self._rows = 0

    def lookupRow(self, index):
        return self.albums[index]

    def lookupRowWrapped(self, index):
        return self.albums[index].wrapped

    def lookupRowIndex(self, index):
        row = self.albums[index]
        first_item_index = row[0].index()
        return first_item_index


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("r3")
    app.setOrganizationDomain("github.com/r3")
    app.setApplicationName("r3tagger")

    form = MainWindow()
    form.show()

    sys.exit(app.exec_())
