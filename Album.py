"""Album Class

Author: r3 (ryan.roler@gmail.com)
Date: 03.17.2012"""

class Album(object):
    """Contains a list of songs and metadata that describes an album"""

    _supported_fields = ('artist', 'album', 'date', 'genre')

    def __init__(self, tracks):
        self.album = None
        self.artist = None
        self.date = None
        self.genre = None

        self.tracks = tracks

        self._find_shared_tags()

    def __call__(self):
        """Saves update metadata for the songs in this album"""
        for song in self:
            song()

    def __iter__(self):
        for song in self.tracks:
            yield song

    def _find_shared_tags(self):
        """Determines the fields that are shared between each of the Album's
        songs. Stored as sets in a dict keyed on the field name:

        dict(artist='someArtist', album='someAlbum' ... )
        """

        def add_fields_from_song(song):
            for field in Album._supported_fields:
                tag = getattr(song, field).pop()
                print tag
                tracker.setdefault(field, set()).add(tag)

        def is_shared(field_set):
            return len(field_set) == 1

        tracker = dict()

        for song in self.tracks:
            add_fields_from_song(song)

        for name, field in tracker.items():
            if is_shared(field):
                tag = field.pop()
                setattr(self, name, tag)
