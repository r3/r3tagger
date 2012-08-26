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
        fileSystemRoot = self.fileSystemModel.setRootPath('/home/ryan/Programming/Python/projects/r3tagger/r3tagger/tests')

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
        self.albumView.expanded.connect(self.fixAlbumViewColumns)
        self.albumView.collapsed.connect(self.fixAlbumViewColumns)

        model = self.albumView.model()
        model.dataChanged.connect(self.updateEditing)

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

        self.tagsToAttribs = {'artist': self.lineArtist,
                              'album': self.lineAlbum,
                              'title': self.lineTitle,
                              'tracknumber': self.lineTrack,
                              'date': self.lineDate,
                              'genre': self.lineGenre}

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

        # Confirm / Cancel / Clear Group
        self.buttonGroup = QHBoxLayout()
        self.buttonGroup.addStretch()
        confirm = QPushButton("Confirm")
        confirm.clicked.connect(self.retagSelected)
        self.buttonGroup.addWidget(confirm)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.cancelChanges)
        self.buttonGroup.addWidget(cancel)
        clear = QPushButton("Clear")
        clear.clicked.connect(self.clearAlbumView)
        self.buttonGroup.addWidget(clear)
        self.buttonGroup.addStretch()

        # Final Layout
        centralWidget = QWidget()
        centralLayout = QVBoxLayout()
        centralLayout.addWidget(self.albumView)
        centralLayout.addLayout(self.buttonGroup)
        centralWidget.setLayout(centralLayout)
        self.setCentralWidget(centralWidget)

    def _fixColumns(self, index, view, model):
        for column in range(model.columnCount(index)):
            view.resizeColumnToContents(column)

    def fixFileSystemColumns(self, index):
        self._fixColumns(index, self.fileSystemView, self.fileSystemModel)

    def fixAlbumViewColumns(self, index):
        model = self.albumView.model()
        self._fixColumns(index, self.albumView, model)

    def updateAlbumModel(self, index):
        path = self.fileSystemModel.fileInfo(index).absoluteFilePath()
        self.addPath(path)

    def addPath(self, path):
        if os.path.isfile(path):
            track = Controller.build_track(path)
            containerAlbum = Controller.album_from_tracks([track], 'Single')
            self.albumView.model().addAlbum(containerAlbum)

        else:
            for album in Controller.build_albums(path, recursive=True):
                self.albumView.model().addAlbum(album)

    def updateEditing(self, index):
        self.albumView.correctListingSelection(index)

        selectedTracks = self.albumView.selectedTracks()
        albumOfSingles = Controller.album_from_tracks(selectedTracks)
        selected = self.albumView.selectedAlbums()
        selected.append(albumOfSingles)
        tags = Controller.find_shared_tags(*selected) if selected else {}

        for tag, edit in self.tagsToAttribs.items():
            if not tags:
                self.clearEditing()
                break
            edit.setText(tags.get(tag, ''))
            edit.setCursorPosition(0)

    def retagSelected(self):
        tags = {}
        for field, lineEdit in self.tagsToAttribs.items():
            tag = lineEdit.text()
            if tag:
                tags[field] = tag

        view = self.albumView

        for album in view.selectedAlbums():
            Controller.retag_album(album, tags)

        for track in view.selectedTracks():
            Controller.retag_track(track, tags)

        for track in self.albumView.model():
            if track.dirty:
                import ipdb
                ipdb.set_trace()  # XXX BREAKPOINT
                track.saveChanges()

    def clearAlbumView(self):
        model = self.albumView.model()
        model.clear()
        model.setHeaders()

    def clearEditing(self):
        for lineEdit in self.tagsToAttribs.values():
            lineEdit.setText('')

    def cancelChanges(self):
        model = self.albumView.model()
        for track in model:
            track.reset()

        model.beginResetModel()
        model.endResetModel()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("r3")
    app.setOrganizationDomain("github.com/r3")
    app.setApplicationName("r3tagger")

    form = MainWindow()
    form.show()

    sys.exit(app.exec_())
