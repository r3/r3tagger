import bisect
from collections import OrderedDict
from functools import total_ordering

from PySide.QtCore import QAbstractItemModel, QModelIndex, Qt
from PySide.QtGui import QTreeView, QItemSelectionModel, QItemSelection

COLUMNS = OrderedDict({"Artist": 'artist',
                       "Album": 'album',
                       "Title": 'title',
                       "Track Number": 'tracknumber',
                       "Date": 'date',
                       "Genre": 'genre'})


@total_ordering
class Node(object):
    def __lt__(self, other):
        return str(self) < str(other)

    def __eq__(self, other):
        return str(self) == str(other)


class AlbumNode(Node):
    def __init__(self, wrapped, parent=None):
        self.wrapped = wrapped
        self.parent = parent
        self.tracks = []

    def __str__(self):
        return self.wrapped.album

    def __len__(self):
        return len(self.tracks)

    def childAtRow(self, row):
        return self.tracks[row]

    def rowOfChild(self, child):
        index = 0
        while self.tracks[index] is not child:
            index = bisect.bisect_left(self.tracks, child, index + 1)

            if index == len(self.tracks) or index == -1:
                return -1

        return index

    def insertChild(self, child):
        child.parent = self
        bisect.insort(self.tracks, child)


class TrackNode(Node):
    def __init__(self, wrapped, parent=None):
        self.parent = parent
        self.wrapped = wrapped

    def __str__(self, separator="\t"):
        fields = [getattr(self.wrapped, x) for x in COLUMNS.values()]
        return separator.join(fields)


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
        columnNumber = index.column()
        field = COLUMNS.values()[columnNumber]
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
        parent = node.parent

        if parent is None:
            return QModelIndex()

        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()

        row = grandparent.rowOfChild(parent)
        return self.createIndex(row, 0, parent)

    def nodeFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self.root


class MusicCollectionView(QTreeView):
    def __init__(self, parent=None):
        super(MusicCollectionView, self).__init__(parent)
        self.setModel(MusicCollectionModel())
        self.setUniformRowHeights(True)

    def _selectedNodes(self):
        # TODO: Cache this maybe? Invalidate cache when new selection made
        return {self.model().nodeFromIndex(x) for x in self.selectedIndexes()}

    def _nodeSiblings(self, node):
        return node.parent.tracks if node.parent else []

    def _siblingsSelected(self, node):
        selected = self._selectedNodes()
        siblings = self._nodeSiblings(node)

        if len(siblings) == 1:
            return True

        return all([x in selected for x in siblings])

    def _childrenSelected(self, node):
        assert isinstance(node, AlbumNode)
        selected = self._selectedNodes()
        return all([x in selected for x in node.tracks])

    def _selectChildren(self, index, selectionPolicy):
        selectionModel = self.selectionModel()
        model = self.model()
        node = model.nodeFromIndex(index)
        assert isinstance(node, AlbumNode)

        topLeft = model.index(0, 0, index)
        bottomRight = model.index(len(node.tracks) - 1,
                                  len(COLUMNS) - 1, index)
        selection = QItemSelection(topLeft, bottomRight)
        selectionModel.select(selection, selectionPolicy)

    def _selectParent(self, index, selectionPolicy):
        selectionModel = self.selectionModel()
        model = self.model()
        parentIndex = index.parent()
        ancestorIndex = parentIndex.parent()

        left = model.index(parentIndex.row(), 0, ancestorIndex)
        right = model.index(parentIndex.row(),
                            len(COLUMNS) - 1, ancestorIndex)

        selection = QItemSelection(left, right)
        selectionModel.select(selection, selectionPolicy)

    def selectedTracks(self):
        result = []
        for node in self._selectedNodes():

            if not isinstance(node, TrackNode):
                continue

            if not self._siblingsSelected(node) or len(self._nodeSiblings(node)) == 1:
                result.append(node.wrapped)

        return result

    def selectedAlbums(self):
        result = []
        for node in self._selectedNodes():
            if isinstance(node, AlbumNode):
                result.append(node.wrapped)
        return result

    def correctListingSelection(self, index):
        print("Selected Tracks: {}\nSelected Albums: {}\n\n".format(self.selectedTracks(), self.selectedAlbums()))
        node = self.model().nodeFromIndex(index)
        selectedNodes = self._selectedNodes()

        if isinstance(node, AlbumNode):
            if node in selectedNodes:
                self._selectChildren(index, QItemSelectionModel.Select)
            elif self._childrenSelected(node):
                self._selectChildren(index, QItemSelectionModel.Deselect)

        elif node in selectedNodes:
            parentNode = self.model().nodeFromIndex(index.parent())
            if self._siblingsSelected(node) and not parentNode in selectedNodes:
                self._selectParent(index, QItemSelectionModel.Select)

        else:
            self._selectParent(index, QItemSelectionModel.Deselect)
