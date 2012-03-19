"""Song Class

Author: r3 (ryan.roler@gmail.com)
Date: 03.17.2012"""

import os.path

from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis

class Song(object):
    """Path to a file and metadata that represents a song"""

    _supported_fields = ('artist', 'title', 'tracknumber', 'date', 'genre')
    _supported_filetypes = {'flac':FLAC, 'ogg':OggVorbis}

    def __init__(self, path, fields=None):
        """Instantiate Song object

        Requires a filepath for a song file to represent and accepts an
        optional fields parameter for specifying the songs fields. If
        such a dictionary is passed, it will be used exclusively to fill
        the field tag data of the Song instance.

        If no additional fields are specified, the Song instance's fields
        will be populated by metadata from the audio file.

        Compatible files: flac (*.flac), ogg vorbis (*.ogg)
        """

        self._song_file = None
        self.path = path

        if fields:
            for field in Song._supported_fields:
                setattr(self, field, fields.get(field, None))
        else:
            self._get_fields_from_file()

    def _connect_to_file(self):
        def determine_type():
            extension = os.path.splitext(self.path)[-1][1:]
            return Song._supported_filetypes[extension]

        song_type = determine_type()
        self._song_file = song_type(self.path)

    def _get_fields_from_file(self):
        if not self._song_file:
            self._connect_to_file()

        for field in Song._supported_fields:
            # Mutagen returns tags as unicode in a list.
            setattr(self, field, self._song_file.get(field, [None])[0])
