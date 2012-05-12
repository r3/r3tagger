"""Album Class

Author: r3 (ryan.roler@gmail.com)
Date: 03.17.2012"""

import difflib


class Album(object):
    """Contains a list of songs and metadata that describes an album.
       May be instantiated either using a collection of Song objects,
       or a dictionary of attribute values. Typically, such a populated
       dictionary might be returned by an external library in attempts
       to describe an album for comparison with another album.
    """

    _supported_fields = ('artist', 'album', 'date', 'genre')

    def __init__(self, arg):
        if isinstance(arg, dict):
            for attrib in ('album', 'artist', 'date', 'genre', 'tracks'):
                setattr(self, attrib, arg.get(attrib, None))
        else:
            self.album = None
            self.artist = None
            self.date = None
            self.genre = None

            self.tracks = arg

            self._find_shared_tags()

    def __call__(self):
        """Saves update metadata for the songs in this album"""
        for song in self:
            song()

    def __iter__(self):
        return iter(self.tracks)

    def _find_shared_tags(self):
        """Determines the fields that are shared between each of the Album's
           songs. Stored as sets in a dict keyed on the field name:

                dict(artist='someArtist', album='someAlbum' ... )
        """

        def add_fields_from_song(song):
            for field in Album._supported_fields:
                tag = getattr(song, field)
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

    def match(self, other):
        """Determines the match quality between self and another Album based
           on attributes: Artist, album, date, genre, and tracks. If a field
           is None in either compared Album, that attribute is not compared.
           A float between 0.0 and 1.0 representing the quality of the match
           will be returned.
        """
        first = []
        second = []

        for attrib in Album._supported_fields:
            if hasattr(self, attrib) and hasattr(other, attrib):
                first.append(getattr(self, attrib))
                second.append(getattr(other, attrib))

        if hasattr(self, 'tracks') and hasattr(other, 'tracks'):
            first.append(''.join([str(x) for x in getattr(self, 'tracks')]))
            second.append(''.join([str(x) for x in getattr(other, 'tracks')]))

        return difflib.SequenceMatcher(None, first, second).ratio()
