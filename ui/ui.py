import bisect
from collections import namedtuple, OrderedDict
from PySide.QtCore import (QAbstractItemModel, QModelIndex, Qt)

Record = namedtuple('Record', ('key', 'node'))

COLUMNS = OrderedDict({"Artist": 'artist',
                       "Album": 'album',
                       "Title": 'title',
                       "Track Number": 'tracknumber',
                       "Date": 'date',
                       "Genre": 'genre'})


class AlbumNode(object):
    def __init__(self, wrapped, parent=None):
        self.wrapped = wrapped
        self.parent = parent
        self.tracks = []

    def __str__(self):
        return self.wrapped.album

    def __len__(self):
        return len(self.tracks)

    def orderKey(self):
        name = self.wrapped.album
        return name.lower() if name else ''

    def childAtRow(self, row):
        return self.tracks[row].node

    def rowOfChild(self, child):
        for i, item in enumerate(self.tracks):
            if item.node == child:
                return i
        return -1

    def childWithKey(self, key):
        """Find node child with given key"""
        if not self.tracks:
            return None
        # Causes a -3 deprecation warning. Solution will be to
        # reimplement bisect_left and provide a key function.
        i = bisect.bisect_left(self.tracks, (key, None))
        if i < 0 or i >= len(self.tracks):
            return None
        if self.tracks[i].key == key:
            return self.tracks[i].node
        return None

    def insertChild(self, child):
        child.parent = self
        bisect.insort(self.tracks, Record(child.orderKey(), child))

    def hasTracks(self):
        if not self.tracks:
            return False
        return isinstance(self.tracks[0], TrackNode)


class TrackNode(object):
    def __init__(self, wrapped, parent=None):
        self.parent = parent
        self.wrapped = wrapped

    def __str__(self, separator="\t"):
        return separator.join(self.fields)

    def __len__(self):
        return len(self.fields)

    @property
    def fields(self):
        return [getattr(self.wrapped, x) for x in COLUMNS.values()]

    def orderKey(self):
        return "\t".join(self.fields).lower()

    def field(self, column):
        assert 0 <= column <= len(self.fields)
        return COLUMNS[column]


class MusicCollectionModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(MusicCollectionModel, self).__init__(parent)
        self.columns = len(COLUMNS)
        self.root = AlbumNode("")
        self.headers = COLUMNS.keys()

    def addAlbum(self, album, callReset=True):
        root = self.root
        albumNode = AlbumNode(album)
        root.insertChild(albumNode)

        for track in album:
            trackNode = TrackNode(track, albumNode)
            albumNode.insertChild(trackNode)

        if callReset:
            self.reset()

    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None or isinstance(node, TrackNode):
            return 0
        return len(node)

    def columnCount(self, parent):
        return self.columns

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignTop | Qt.AlignLeft)
        if role != Qt.DisplayRole:
            return None
        node = self.nodeFromIndex(index)
        assert node is not None
        if isinstance(node, AlbumNode):
            return str(node) if index.column() == 0 else ""
        column_number = index.column()
        field = COLUMNS.values()[column_number]
        return getattr(node.wrapped, field)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            assert 0 <= section <= len(self.headers)
            return self.headers[section]
        return None

    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column, branch.childAtRow(row))

    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)

    def nodeFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self.root
