"""Controller

    Handles the processing of Albums of Song objects. Host to the recognition
    algorithms and querier of the Musicbrainz database
"""

#import queries
import os
from Album import Album
from Song import Song


def build_albums(path, recursive=False):
    if recursive is False:
        for _, _, files in os.walk(path):
            yield Album([Song(os.path.join(path, x)) for x in files])
    else:
        files = os.listdir(path)
        yield Album([Song(os.path.join(path, x)) for x in files])
