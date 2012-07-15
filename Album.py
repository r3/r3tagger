"""Album Class

Author: r3 (ryan.roler@gmail.com)
Date: 03.17.2012"""


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

    # TODO: Refactor into controller?
    def _find_shared_tags(self):
        """Determines the fields that are shared between each of the Album's
           songs and adds these to the Album's fields.
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
        """Compares albums based on supported fields
        This implementation will only take tracks into account if both
        Album objects have tracks. If only one, or neither have tracks,
        only the supported fields (Album._supported_fields) are used.
        """

        fields = self.__class__._supported_fields
        albums = []

        for album in (self, other):
            info = {getattr(album, field) for field in fields}
            if self.tracks and other.tracks:
                info.update([str(x) for x in album.tracks])
            albums.append(info)

        first, second = albums

        nc = len(first.intersection(second))
        na = len(first)
        nb = len(second)

        return float(nc) / (na + nb - nc)
