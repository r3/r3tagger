"""Controller

    Handles the processing of Albums of Song objects. Host to the recognition
    algorithms and querier of the Musicbrainz database
"""

import os
import shutil
#from queries import Musicbrainz

from Album import Album
from Song import Song


def _set_album_path(album, path):
    album.path = path

    for track in album:
        if '/' in track.path:
            name = os.path.split(track.path)[-1]
        else:
            name = track.path

        track.path = os.path.join(path, name)


def build_albums(path, recursive=False):
    if recursive is False:
        files = [os.path.join(path, x) for x in os.listdir(path)]
        album = Album([Song(x) for x in files if os.path.isfile(x)])
        _set_album_path(album, path)
        yield album
    else:
        for root, _, files in os.walk(path):
            tracks = [os.path.join(path, x) for x in files]
            album = Album([Song(x) for x in tracks if os.path.isfile(x)])
            _set_album_path(album, root)
            yield album


def rename_album(album, pattern=None):
    # TODO: Move into a config
    default_pattern = "{date} - {album}"

    if pattern is None:
        pattern = default_pattern

    supported_fields = album.__class__._supported_fields
    fields = {field: getattr(album, field) for field in supported_fields}
    name = pattern.format(**fields)

    if album.path.endswith(os.path.sep):
        album_path = os.path.dirname(album.path)
        root_path = os.path.dirname(album_path)
    else:
        root_path = os.path.dirname(album.path)

    destination = os.path.join(root_path, name)

    if not os.path.exists(destination):
        shutil.move(album.path, destination)

    _set_album_path(album, destination)


def rename_tracks(album, pattern=None):
    pass
