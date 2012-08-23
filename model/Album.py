"""r3tagger.model.Album

Provides models:
    Album
    Represents an album of Tracks
"""


class Album(object):
    """Contains a list of track and metadata that describes an album.

    May be instantiated either using a collection of Track objects,
    or a dictionary of attribute values. Typically, such a populated
    dictionary might be returned by an external library in attempts
    to describe an album for comparison with another album.

    Provides Methods:
        match(other:Album)
        Provides a rating of similarity with another Album in [0, 1]

        Album.supported_fields()
        Class method accessor for discovering string representations of
        fields supported by the Album (eg. 'artist', 'album', 'genre')
    """

    _supported_fields = ('artist', 'album', 'date', 'genre')

    def __init__(self, arg):
        if isinstance(arg, dict):
            for attrib in self.supported_fields():
                setattr(self, attrib, arg.get(attrib, ''))
            self.tracks = arg.get('tracks', [])
        else:
            self.path = ''
            self.album = ''
            self.artist = ''
            self.date = ''
            self.genre = ''
            self.tracks = arg

    def __call__(self):
        """Passes call to each Track in the Album"""
        for track in self:
            track()

    def __iter__(self):
        return iter(self.tracks)

    def __getitem__(self, index):
        return self.tracks[index]

    def match(self, other):
        """Compares albums based on supported fields

        This implementation will only take tracks into account if both
        Album objects have tracks. If only one, or neither have tracks,
        only the supported fields (Album._supported_fields) are used.
        """

        albums = []

        info = set()
        other_info = set()

        for field in self.supported_fields():
            attrib = getattr(self, field)
            other_attrib = getattr(other, field)
            if attrib and other_attrib:
                info.add(attrib)
                other_info.add(other_attrib)

            if self.tracks and other.tracks:
                info.update([str(x) for x in self.tracks if x])
                other_info.update([str(x) for x in other.tracks if x])

        print(albums)

        nc = len(info.intersection(other_info))
        na = len(info)
        nb = len(other_info)

        return float(nc) / (na + nb - nc)

    @classmethod
    def supported_fields(cls):
        """Determine the supported fields of the Album

        example result: ('artist', 'album', 'genre')
        """
        return cls._supported_fields
