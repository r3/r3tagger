"""Song Class

Author: r3 (ryan.roler@gmail.com)
Date: 03.17.2012"""

import os.path

from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC


class Song(object):
    """Path to a file and metadata that represents a song"""

    _supported_fields = ('artist', 'album', 'title',
                         'tracknumber', 'date', 'genre')

    _supported_filetypes = {'flac': FLAC, 'ogg': OggVorbis}

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

        self.path = path
        self._song_file = None
        self._connect_to_file()

        # Fill in tags if given a dict
        if fields is not None:
            for field in Song._supported_fields:
                self._song_file[field] = fields.get(field, None)

    def __call__(self):
        """Shortcut to _update_file: Saves updated metadata to file."""
        self._update_file()

    def __setattr__(self, attr, val):
        if attr in Song._supported_fields:
            self._song_file[attr] = val
        else:
            self.__dict__[attr] = val

    def __getattr__(self, attr):
        if attr in Song._supported_fields:
            return self._song_file.get(attr, '')
        else:
            return self.__dict__[attr]

    def _connect_to_file(self):
        """Opens a file and determines type. File will be opened
        (if compatible) with codec and metadata will be read in.
        """
        def determine_type():
            """Determine codec to use in opening file depending on extension"""
            extension = os.path.splitext(self.path)[-1][1:]
            return Song._supported_filetypes[extension]

        song_type = determine_type()
        self._song_file = song_type(self.path)

    def _update_file(self):
        """Saves updated metadata to file."""
        self._song_file.save()

    @property
    def length(self):
        """Song length in seconds"""
        return self._song_file.info.length

    @property
    def bitrate(self):
        """Bitrate of song (160000)"""
        return self._song_file.info.bitrate
