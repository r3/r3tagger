import sys
from collections import namedtuple

from PySide.QtGui import (QStandardItemModel, QStandardItem, QMainWindow,
                          QTableView, QApplication, QAbstractItemView)


row_object = namedtuple('row_object', ('model', 'view', 'parent'))


class AlbumCollectionModel(QStandardItemModel):
    def __init__(self, parent=None):
        super(AlbumCollectionModel, self).__init__(parent)

        self._rows = 0
        self._albums = {}
        self.columns = ("title", "artist", "album", "track_number")

    def addAlbum(self, album):
        album_row = self._build_row(album)
        self._albums[self._rows] = row_object(album, album_row, None)
        self.appendRow(album_row)

        for track in album:
            track_row = self._build_row(track)
            self._albums[self._rows] = row_object(track, track_row, album)
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

    def lookupRowData(self, index):
        return self._albums[index].model

    def lookupRowIndex(self, index):
        return self._albums[index].view[0].index()


class Album(object):
    def __init__(self, title, tracks):
        self.title = title
        self.tracks = tracks

    def __iter__(self):
        return iter(self.tracks)


class Track(object):
    def __init__(self, artist, album, track_number):
        self.artist = artist
        self.album = album
        self.track_number = track_number


class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # Model
        self.model = AlbumCollectionModel()

        # Views
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().hide()

        self.setCentralWidget(self.table)

        # Populate model
        for album in buildAlbums():
            self.model.addAlbum(album)

        self.table.clicked.connect(self.testShit)

    def selectedRows(self):
        return {x.row() for x in self.table.selectedIndexes()}

    def testShit(self):
        index = self.selectedRows().pop()
        #self.table.selectRow(index + 1)
        print(index)


def buildAlbums():
    artist = "artist"
    album = "album"
    tracks = [Track(artist, album, str(x)) for x in range(10)]
    album = Album(album, tracks)

    return [album]


if __name__ == '__main__':
    app = QApplication(sys.argv)

    form = Window()
    form.show()

    sys.exit(app.exec_())
