import sys
import os

from PySide.QtCore import Qt, QModelIndex
from PySide.QtGui import (QTreeView, QMainWindow, QFileSystemModel, QAction,
                          QDockWidget, QAbstractItemView, QHBoxLayout, QIcon,
                          QVBoxLayout, QWidget, QLineEdit, QPushButton,
                          QApplication, QFormLayout, QKeySequence,
                          QMessageBox)

import AlbumCollection
from r3tagger import Controller
import qrc_resources


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.dirty = False

        # Models
        #  - Filesystem Model
        self.fileSystemModel = QFileSystemModel()
        #rootPath = QDesktopServices.storageLocation(
            #QDesktopServices.HomeLocation)
        #fileSystemRoot = self.fileSystemModel.setRootPath(rootPath)
        fileSystemRoot = self.fileSystemModel.setRootPath(
            '/home/ryan/Programming/Python/projects/r3tagger/r3tagger/tests')

        # Views
        #  - Filesystem View
        self.fileSystemView = QTreeView()
        self.fileSystemView.setModel(self.fileSystemModel)
        self.fileSystemView.setRootIndex(fileSystemRoot)
        self.fileSystemView.doubleClicked.connect(self.updateAlbumModel)
        self.fileSystemView.expanded.connect(self.fixFileSystemColumns)
        self.fileSystemView.collapsed.connect(self.fixFileSystemColumns)
        #  - Album View
        self.albumView = AlbumCollection.MusicCollectionView()
        self.albumView.setSelectionMode(QAbstractItemView.MultiSelection)
        self.albumView.clicked.connect(self.updateEditing)
        self.albumView.expanded.connect(self.fixAlbumViewColumns)
        self.albumView.collapsed.connect(self.fixAlbumViewColumns)
        self.albumView.model().dataChanged.connect(self.fixAlbumViewColumns)
        self.albumView.model().dataChanged.connect(self._setDirty)

        model = self.albumView.model()
        model.dataChanged.connect(self.updateEditing)

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

        # Statusbar
        #status = self.statusBar()
        #status.setSizeGripEnabled(False)
        #status.showMessage("Ready", 5000)

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

        # Actions
        fileOpenAction = self._createAction(
            text="&Open",
            slot=self.fileOpen,
            shortcut=QKeySequence.Open,
            icon='fileOpen',
            tip="Open location")

        fileSaveAction = self._createAction(
            text="&Save",
            slot=self.fileSave,
            shortcut=QKeySequence.Save,
            icon='fileSave',
            tip="Save changes")

        fileQuitAction = self._createAction(
            text="&Quit",
            slot=self.fileQuit,
            shortcut=QKeySequence.Quit,
            icon='fileQuit',
            tip="Quit program")

        editRecognizeAction = self._createAction(
            text="&Recognize",
            slot=self.editRecognize,
            shortcut=QKeySequence(Qt.CTRL + Qt.Key_R),
            icon='editRecognize',
            tip="Recognize music")

        editReorganizeAction = self._createAction(
            text="Reorganize",
            slot=self.editReorganize,
            shortcut=QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_R),
            icon='editReorganize',
            tip="Reorganize music")

        editSettingsAction = self._createAction(
            text="Settings",
            slot=self.editSettings,
            shortcut=QKeySequence.Preferences,
            icon='editSettings',
            tip="Edit settings")

        helpDocsAction = self._createAction(
            text="Documentation",
            slot=self.helpDocs,
            shortcut=QKeySequence.HelpContents,
            icon='helpDocs',
            tip="Documentation")

        helpAboutAction = self._createAction(
            text="About",
            slot=self.helpAbout,
            shortcut=QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_F1),
            icon='helpAbout',
            tip="About")

        toggleEditing = editingDock.toggleViewAction()
        toggleEditing.setIcon(QIcon(":/toggleEditing.png"))

        toggleFileNav = fileSystemDock.toggleViewAction()
        toggleFileNav.setIcon(QIcon(":/toggleFileNav.png"))

        # Menus
        fileMenu = self.menuBar().addMenu("&File")
        self._addActions(fileMenu, (fileOpenAction, fileSaveAction,
                                    fileQuitAction))

        editMenu = self.menuBar().addMenu("&Edit")
        self._addActions(editMenu, (editReorganizeAction,
                                    editRecognizeAction, editSettingsAction))

        helpMenu = self.menuBar().addMenu("&Help")
        self._addActions(helpMenu, (helpDocsAction, helpAboutAction))

        # Toolbars
        fileToolbar = self.addToolBar("FileToolbar")
        fileToolbar.setObjectName("fileToolbar")
        self._addActions(fileToolbar, (fileOpenAction, fileSaveAction))

        editToolbar = self.addToolBar("EditToolbar")
        editToolbar.setObjectName("editToolbar")
        self._addActions(editToolbar, (editRecognizeAction,
                                       editReorganizeAction))

        toggleToolbar = self.addToolBar("ToggleToolbar")
        toggleToolbar.setObjectName("toggleToolbar")
        self._addActions(toggleToolbar, (toggleEditing, toggleFileNav))

        # Final Layout
        centralWidget = QWidget()
        centralLayout = QVBoxLayout()
        centralLayout.addWidget(self.albumView)
        centralLayout.addLayout(self.buttonGroup)
        centralWidget.setLayout(centralLayout)
        self.setCentralWidget(centralWidget)

    def _createAction(self, text, slot=None, shortcut=None, icon=None,
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

    def _addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def _setDirty(self):
        self.dirty = True

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
        self.fixAlbumViewColumns(index)

    def addPath(self, path):
        if os.path.isfile(path):
            track = Controller.build_track(path)
            containerAlbum = Controller.album_from_tracks([track], u'Singles')
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

        self.saveChanges()

    def clearAlbumView(self):
        model = self.albumView.model()
        model.clear()
        model.setHeaders()

    def clearEditing(self):
        for lineEdit in self.tagsToAttribs.values():
            lineEdit.setText('')

    def saveChanges(self):
        for track in self.albumView.model():
            if track.dirty:
                track.saveChanges()

        self.dirty = False
        self.resetModel()

    def cancelChanges(self):
        for track in self.albumView.model():
            track.reset()

        self.resetModel()

    def resetModel(self):
        model = self.albumView.model()
        model.beginResetModel()
        self.clearEditing()

        expanded = []
        rowCount = model.rowCount(QModelIndex())
        for row in range(rowCount):
            index = model.index(row, 0, QModelIndex())
            if self.albumView.isExpanded(index):
                expanded.append(index)

        model.endResetModel()

        for expandedIndex in expanded:
            self.albumView.setExpanded(expandedIndex, True)

    def fileOpen(self):
        pass

    def fileSave(self):
        pass

    def fileQuit(self):
        if self.dirty:
            reply = QMessageBox.question(
                self, "r3tagger - Unsaved Changes",
                "Save unsaved changes?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if reply:
                self.saveChanges()
                self.close()
            else:
                return None

        self.close()

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("r3")
    app.setOrganizationDomain("github.com/r3")
    app.setApplicationName("r3tagger")

    form = MainWindow()
    form.show()

    sys.exit(app.exec_())
