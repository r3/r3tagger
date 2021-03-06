import sys
import os

from PySide.QtCore import Qt, QModelIndex, QSettings
from PySide.QtGui import (QTreeView, QMainWindow, QFileSystemModel, QAction,
                          QDockWidget, QAbstractItemView, QHBoxLayout, QIcon,
                          QVBoxLayout, QWidget, QLineEdit, QPushButton,
                          QApplication, QFormLayout, QKeySequence,
                          QMessageBox, QFileDialog)

import albumcollection
from r3tagger import controller
#import qrc_resources


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
        self.albumView = albumcollection.MusicCollectionView()
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
        confirm.clicked.connect(self.confirmChanges)
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
        fileAddSongAction = self._createAction(
            text="Add &Songs",
            slot=self.fileAddSong,
            shortcut=QKeySequence.Open,
            icon='fileOpen',
            tip="Add files (songs)")

        fileAddAlbumAction = self._createAction(
            text="Add &Album",
            slot=self.fileAddAlbum,
            shortcut=QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_O),
            icon='fileOpen',
            tip="Add directory (album)")

        fileSaveAction = self._createAction(
            text="&Save Changes",
            slot=self.confirmChanges,
            shortcut=QKeySequence.Save,
            icon='fileSave',
            tip="Save Changes")

        fileQuitAction = self._createAction(
            text="&Quit",
            slot=self.close,
            shortcut=QKeySequence.Quit,
            icon='fileQuit',
            tip="Quit Program")

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
        self._addActions(fileMenu, (fileAddSongAction, fileAddAlbumAction,
                                    fileSaveAction, fileQuitAction))

        editMenu = self.menuBar().addMenu("&Edit")
        self._addActions(editMenu, (editReorganizeAction,
                                    editRecognizeAction, editSettingsAction))

        helpMenu = self.menuBar().addMenu("&Help")
        self._addActions(helpMenu, (helpDocsAction, helpAboutAction))

        # Toolbars
        editToolbar = self.addToolBar("EditToolbar")
        editToolbar.setObjectName("editToolbar")
        self._addActions(editToolbar, (editRecognizeAction,
                                       editReorganizeAction))

        toggleToolbar = self.addToolBar("ToggleToolbar")
        toggleToolbar.setObjectName("toggleToolbar")
        self._addActions(toggleToolbar, (toggleFileNav, toggleEditing))

        # Settings
        settings = QSettings()
        if settings.contains("MainWindow/Geometry"):
            self.restoreGeometry(settings.value("MainWindow/Geometry"))

        if settings.contains("MainWindow/State"):
            self.restoreState(settings.value("MainWindow/State"))

        self.setWindowTitle("r3tagger")

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

    def closeEvent(self, event):
        if self.dirty:
            reply = QMessageBox.question(
                self,
                "r3tagger - Unsaved Changes",
                "Save unsaved changes?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if reply == QMessageBox.Cancel:
                event.ignore()
                return None
            elif reply == QMessageBox.Yes:
                self.confirmChanges()

        settings = QSettings()
        settings.setValue("MainWindow/Geometry", self.saveGeometry())
        settings.setValue("MainWindow/State", self.saveState())

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
            track = controller.build_track(path)
            containerAlbum = controller.album_from_tracks([track], u'Singles')
            self.albumView.model().addAlbum(containerAlbum)

        else:
            for album in controller.build_albums(path, recursive=True):
                self.albumView.model().addAlbum(album)

    def updateEditing(self, index):
        self.albumView.correctListingSelection(index)

        selectedTracks = self.albumView.selectedTracks()
        albumOfSingles = controller.album_from_tracks(selectedTracks)
        selected = self.albumView.selectedAlbums()
        selected.append(albumOfSingles)
        tags = controller.find_shared_tags(*selected) if selected else {}

        for tag, edit in self.tagsToAttribs.items():
            if not tags:
                self.clearEditing()
                break
            edit.setText(tags.get(tag, ''))
            edit.setCursorPosition(0)

    def confirmChanges(self):
        tags = {}
        for field, lineEdit in self.tagsToAttribs.items():
            tag = lineEdit.text()
            tags[field] = tag

        view = self.albumView

        for album in view.selectedAlbums():
            controller.retag_album(album, tags)

        for track in view.selectedTracks():
            controller.retag_track(track, tags)

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

    def fileAddSong(self):
        selectedFiles, selectedFilter = QFileDialog.getOpenFileNames(
            parent=self,
            caption="Add Songs")

        for song in selectedFiles:
            self.addPath(song)

    def fileAddAlbum(self):
        selectedDir = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Add Album")

        self.addPath(selectedDir)

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
