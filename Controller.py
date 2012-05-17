"""Controller

    Handles the processing of Albums of Song objects. Host to the recognition
    algorithms and querier of the Musicbrainz database
"""

from os import (listdir, walk)
from os.path import (isfile, join)

from queries import Musicbrainz
from Album import Album
from Song import Song


def build_albums(path, recursive=False):
    if recursive is False:
        files = [join(path, x) for x in listdir(path)]
        yield Album([Song(x) for x in files if isfile(x)])
    else:
        for _, _, files in walk(path):
            tracks = [join(path, x) for x in files]
            yield Album([Song(x) for x in tracks if isfile(x)])
