"""Controller

    Handles the processing of Albums of Track objects. Host to the recognition
    algorithms and querier of the Musicbrainz database
"""

import os
import shutil
#from queries import Musicbrainz

from Album import Album
from Track import Track


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
        album = Album([Track(x) for x in files if os.path.isfile(x)])
        _set_album_path(album, path)
        yield album
    else:
        for root, _, files in os.walk(path):
            tracks = [os.path.join(path, x) for x in files]
            album = Album([Track(x) for x in tracks if os.path.isfile(x)])
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


def rename_tracks(target, pattern=None):
    default_pattern = "{artist} - {tracknumber} - {title}"

    if pattern is None:
        pattern = default_pattern

    def rename_track(track, pattern):
        extension = os.path.splitext(track.path)[-1]
        root = os.path.dirname(track.path)

        supported_fields = track.__class__._supported_fields
        fields = {field: getattr(track, field) for field in supported_fields}
        name = pattern.format(**fields) + extension

        destination = os.path.join(root, name)
        shutil.move(track.path, destination)
        track.path = destination

    try:
        # Try to iterate through target, if you can, it's an Album
        for track in target:
            rename_track(track, pattern)
    except TypeError:
        # If you can't iterate, it's a Track
        rename_track(target, pattern)
