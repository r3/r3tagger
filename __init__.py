"""r3tagger (https://github.com/r3/r3tagger)

author: Ryan Roler (ryan.roler@gmail.com)
license: GPL 3
requires: Python 2.7 -   http://python.org/
          Mutagen -      http://code.google.com/p/mutagen/
          Musicbrainz2 - http://musicbrainz.org/doc/python-musicbrainz2
          Acoustid -     http://acoustid.org/fingerprinter
          Chromaprint -  http://acoustid.org/chromaprint
          PyTest -       http://pytest.org/  # Only needed for tests


This module is intended to provide high level resources to be used in the
r3tagger.

Provides Classes:
    FileExistsError
    Used to indicate that a file exists where the program is trying to write
"""


class FileExistsError(Exception):
    """A file exists where the program is trying to write"""
    pass
