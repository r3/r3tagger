import sys
from collections import OrderedDict

from PySide.QtCore import Qt
from PySide.QtGui import (QStandardItemModel, QStandardItem, QTreeView,
                          QMainWindow, QFileSystemModel, QDockWidget, QLabel,
                          QAbstractItemView, QHBoxLayout, QVBoxLayout,
                          QWidget, QLineEdit, QPushButton, QApplication)

from r3tagger import Controller


columns = OrderedDict({"Artist": 'artist', "Album": 'album', "Title": 'title',
    "Track Number": 'tracknumber', "Date": 'date', "Genre": 'genre'})


class StandardItem(QStandardItem):
    def data(self, column):
        columnName = columns.keys()[column]
        # TODO: Supposes that column order never changes
        field = columns[columnName]
        wrapped = self.data(Qt.UserRole)
        return getattr(wrapped, field)


class AlbumCollectionModel(QStandardItemModel):
    def __init__(self):
        super(AlbumCollectionModel, self).__init__()

        self.albums = []

    def addAlbum(self, album):
        parent = StandardItem()
        parent.setData(album, Qt.UserRole)

        for track in album:
            item = StandardItem()
            item.setData(track, Qt.UserRole)
            parent.appendRow(item)

        self.appendRow(parent)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Models
        #  - Filesystem Model
        self.fileSystemModel = QFileSystemModel()
        # TODO: Set this to CWD and add drives/root
        fileSystemRoot = self.fileSystemModel.setRootPath('/home/ryan/Programming/Python/projects/r3tagger/r3tagger')
        #  - Album Model
        self.albumModel = AlbumCollectionModel()

        # Views
        #  - Filesystem View
        self.fileSystemView = QTreeView()
        self.fileSystemView.setModel(self.fileSystemModel)
        self.fileSystemView.setRootIndex(fileSystemRoot)
        self.fileSystemView.doubleClicked.connect(self.updateAlbumModel)
        #  - Album View
        self.albumView = QTreeView()
        self.albumView.setModel(self.albumModel)
        self.albumView.setSelectionMode(QAbstractItemView.MultiSelection)
        self.albumView.clicked.connect(self.updateEditing)

        # Statusbar
        #status = self.statusBar()
        #status.setSizeGripEnabled(False)
        #status.showMessage("Ready", 5000)

        # Editing Group
        self.editingGroup = QHBoxLayout()
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

        self.editingGroup.addLayout(labels)
        self.editingGroup.addLayout(edits)

        # Docks
        dockAllowed = (Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        #  - Filesystem Dock
        fileSystemDock = QDockWidget("Navigate", self)
        fileSystemDock.setObjectName("fileSystemDock")
        fileSystemDock.setAllowedAreas(dockAllowed)
        fileSystemDock.setWidget(self.fileSystemView)
        self.addDockWidget(Qt.LeftDockWidgetArea, fileSystemDock)
        #  - Editing Dock
        editingWidget = QWidget()
        editingWidget.setLayout(self.editingGroup)
        editingDock = QDockWidget("Editing", self)
        editingDock.setObjectName("editingDock")
        editingDock.setAllowedAreas(dockAllowed)
        editingDock.setWidget(editingWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, editingDock)

        # Confirm / Cancel Group
        self.buttonGroup = QHBoxLayout()
        self.buttonGroup.addStretch()
        self.buttonGroup.addWidget(QPushButton("Confirm"))
        self.buttonGroup.addWidget(QPushButton("Cancel"))
        self.buttonGroup.addStretch()

        # Final Layout
        centralWidget = QWidget()
        centralLayout = QVBoxLayout()
        centralLayout.addWidget(self.albumView)
        centralLayout.addLayout(self.buttonGroup)
        centralWidget.setLayout(centralLayout)
        self.setCentralWidget(centralWidget)

    def updateAlbumModel(self):
        path = 'get path!'
        for album in Controller.build_albums(path):
            self.albumModel.addAlbum(album)

    def updateEditing(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("r3")
    app.setOrganizationDomain("github.com/r3")
    app.setApplicationName("r3tagger")

    form = MainWindow()
    form.show()

    sys.exit(app.exec_())
