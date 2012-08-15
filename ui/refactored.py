import sys

from PySide.QtCore import Qt
from PySide.QtGui import (QTreeView, QMainWindow, QFileSystemModel,
                          QDockWidget, QLabel, QAbstractItemView, QHBoxLayout,
                          QVBoxLayout, QWidget, QLineEdit, QPushButton,
                          QApplication)

from r3tagger import Controller
import ui


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Models
        #  - Filesystem Model
        self.fileSystemModel = QFileSystemModel()
        # TODO: Set this to CWD and add drives/root
        fileSystemRoot = self.fileSystemModel.setRootPath('/home/ryan/Programming/Python/projects/r3tagger/r3tagger')

        # Views
        #  - Filesystem View
        self.fileSystemView = QTreeView()
        self.fileSystemView.setModel(self.fileSystemModel)
        self.fileSystemView.setRootIndex(fileSystemRoot)
        self.fileSystemView.doubleClicked.connect(self.updateAlbumModel)
        #  - Album View
        self.albumView = ui.MusicCollectionView()
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

    def updateAlbumModel(self, index):
        path = self.fileSystemModel.fileInfo(index).absoluteFilePath()
        for album in Controller.build_albums(path, recursive=True):
            self.albumView.model().addAlbum(album)

    def updateEditing(self, index):
        self.albumView.correctListingSelection(index)

        tags_to_attribs = {'artist': self.lineArtist,
                           'album': self.lineAlbum,
                           'title': self.lineTitle,
                           'tracknumber': self.lineTrack,
                           'date': self.lineDate,
                           'genre': self.lineGenre}

        selectedTracks = self.albumView.selectedTracks()
        albumOfSingles = Controller.album_from_tracks(selectedTracks)
        selected = self.albumView.selectedAlbums()
        selected.append(albumOfSingles)
        tags = Controller.find_shared_tags(*selected) if selected else {}

        for tag, edit in tags_to_attribs.items():
            edit.setText(tags.get(tag, ''))

        if len(selectedTracks) == 1:
            track = selectedTracks[0]
            self.lineTitle.setText(track.title)
            self.lineTrack.setText(track.tracknumber)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("r3")
    app.setOrganizationDomain("github.com/r3")
    app.setApplicationName("r3tagger")

    form = MainWindow()
    form.show()

    sys.exit(app.exec_())
