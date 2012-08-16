import sys
import os

from PySide.QtCore import Qt
from PySide.QtGui import (QTreeView, QMainWindow, QFileSystemModel,
                          QDockWidget, QAbstractItemView, QHBoxLayout,
                          QVBoxLayout, QWidget, QLineEdit, QPushButton,
                          QApplication, QFormLayout)

import ui
from r3tagger import Controller


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
        self.fileSystemView.expanded.connect(self.fixFileSystemColumns)
        self.fileSystemView.collapsed.connect(self.fixFileSystemColumns)
        #  - Album View
        self.albumView = ui.MusicCollectionView()
        self.albumView.setSelectionMode(QAbstractItemView.MultiSelection)
        self.albumView.clicked.connect(self.updateEditing)

        # Statusbar
        #status = self.statusBar()
        #status.setSizeGripEnabled(False)
        #status.showMessage("Ready", 5000)

        # Editing Group
        self.editingGroup = QFormLayout()
        self.lineArtist = QLineEdit()
        self.lineAlbum = QLineEdit()
        self.lineTitle = QLineEdit()
        self.lineTrack = QLineEdit()
        self.lineDate = QLineEdit()
        self.lineGenre = QLineEdit()
        self.editingGroup.addRow("Artist:", self.lineArtist)
        self.editingGroup.addRow("Album:", self.lineAlbum)
        self.editingGroup.addRow("Title:", self.lineTitle)
        self.editingGroup.addRow("Track:", self.lineTrack)
        self.editingGroup.addRow("Date:", self.lineDate)
        self.editingGroup.addRow("Genre:", self.lineGenre)

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

    def fixFileSystemColumns(self, index):
        columns = self.fileSystemModel.columnCount(index)
        for column in range(columns):
            self.fileSystemView.resizeColumnToContents(column)

    def updateAlbumModel(self, index):
        path = self.fileSystemModel.fileInfo(index).absoluteFilePath()

        if os.path.isfile(path):
            track = Controller.build_track(path)
            containerAlbum = Controller.album_from_tracks([track], 'Single')
            self.albumView.model().addAlbum(containerAlbum)

        else:
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
