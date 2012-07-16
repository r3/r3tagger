"""r3tagger.Controller

Handles the processing and construction of Albums of Tracks

Provided Functions:
    build_albums(album:Album, path:str)
    Produce iterables of Albums on path

    find_shared_tags(album:Album)
    Collects shard fields into a dict

    rename_album(album:Album)
    Renames an Album

    rename_tracks(target:model)
    Renames Track or Tracks in an Album
"""

import os
import shutil

from r3tagger.model.Album import Album
from r3tagger.model.Track import Track


def _set_album_path(album, path):
    """Correct a path to an Album or add a new one"""
    album.path = path

    for track in album:
        if '/' in track.path:
            name = os.path.split(track.path)[-1]
        else:
            name = track.path

        track.path = os.path.join(path, name)


def build_albums(path, recursive=False):
    """Provides an iterable of Albums based on a path

    build_albums provides an optional parameter: recursive.
    If recursive is set to True, Albums will be created from
    the given path, as well as any subdirectories. The
    default is False, and so only one Album is created for
    the iterable result.
    """
    def prep_album(files, path):
        """An attempt to keep code affecting the build of an Album"""
        tracks = [os.path.join(path, x) for x in files]
        album = Album([Track(x) for x in tracks if os.path.isfile(x)])
        _set_album_path(album, path)

        for field, shared_value in find_shared_tags(album).items():
            setattr(album, field, shared_value)

        return album

    if recursive is False:
        yield prep_album(os.listdir(path), path)
    else:
        for root, _, files in os.walk(path):
            yield prep_album(files, root)


def rename_album(album, pattern=None):
    """Correct the folder of an album to reflect tags and a given pattern

    A pattern may be passed as an argument, but rename_album will use the
    configuration files to select one.

    The paths of any Tracks contained by the album will make the necessary
    changes to remain valid.

    Note: Default pattern is currently hardcoded
    """
    # TODO: Move into a config
    default_pattern = "{date} - {album}"

    if pattern is None:
        pattern = default_pattern

    supported_fields = album.supported_fields()
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
    """Correct the file name of a Track to reflect tags and a given pattern

    A pattern may be passed as an argument, but rename_tracks will use the
    configuration files to select one.

    Pattern Example: '{artist} - {tracknumber} - {title}'

    Supported fields my be retreived with:
    r3tagger.model.Track.supported_fields()

    Note: Default pattern is currently hardcoded
    Note: Supported Fields method doesn't yet exist, use _supported_fields
    """
    default_pattern = "{artist} - {tracknumber} - {title}"

    if pattern is None:
        pattern = default_pattern

    def rename_track(track, pattern):
        extension = os.path.splitext(track.path)[-1]
        root = os.path.dirname(track.path)

        supported_fields = track.supported_fields()
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


def find_shared_tags(album):
    """Finds field shared by all tracks on a given album
    Returns a dictionary mapping of fields to shared values.
    """
    def is_shared(field, album):
        if len({getattr(x, field) for x in album.tracks}) == 1:
            return field

    result = {}

    for field in album.supported_fields():
        if is_shared(field, album):
            result[field] = getattr(album.tracks[0], field)

    return result
