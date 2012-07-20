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

    retag_album(album:Album, mapping:dict)
    Retag an Album and contents based on a mapping

    retag_track(track:Track, mapping:dict)
    Retag a Track based on a mapping

    missing_fields(target:Album|Track)
    Returns list of fields that have missing tags
"""

import os
import shutil
import ConfigParser

from mutagen import File

from r3tagger import FileExistsError
from r3tagger.model.Album import Album
from r3tagger.model.Track import Track
from r3tagger.library import filename, parent, extension

# Configuration loading
config_file = os.path.join(os.path.dirname(__file__), 'r3tagger.cfg')
config = ConfigParser.RawConfigParser()
config.read(config_file)

THRESHOLD = config.get('Main', 'match-threshold')
TRACK_PATTERN = config.get('Main', 'track-pattern')
ALBUM_PATTERN = config.get('Main', 'album-pattern')


# Classes
class NoFileFoundError(Exception):
    pass


# Functions
def _set_album_path(album, path):
    """Correct a path to an Album or add a new one"""
    album.path = path

    for track in album:
        track.path = os.path.join(path, filename(track.path))


def build_track(path):
    """Create a Track based on a path"""
    if os.path.isfile(path):
        return Track(path)
    else:
        raise NoFileFoundError("No file exists at {}".format(path))


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
        paths = [os.path.join(path, x) for x in files]
        tracks = [Track(x) for x in paths if os.path.isfile(x) and File(x)]

        if not tracks:
            raise NoFileFoundError("No supported tracks at {}".format(path))

        album = Album(tracks)
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
    """
    if pattern is None:
        pattern = ALBUM_PATTERN

    supported_fields = album.supported_fields()
    fields = {field: getattr(album, field) for field in supported_fields}
    name = pattern.format(**fields)

    album_parent = parent(album.path)

    destination = os.path.join(album_parent, name)

    if not os.path.exists(destination):
        shutil.move(album.path, destination)
    else:
        raise FileExistsError("File exists: {}".format(destination))

    _set_album_path(album, destination)


def rename_tracks(target, pattern=None):
    """Correct the file name of a Track to reflect tags and a given pattern

    A pattern may be passed as an argument, but rename_tracks will use the
    configuration files to select one.

    Pattern Example: '{artist} - {tracknumber} - {title}'
    """
    if pattern is None:
        pattern = TRACK_PATTERN

    def rename_track(track, pattern):
        supported_fields = track.supported_fields()
        fields = {field: getattr(track, field) for field in supported_fields}
        name = pattern.format(**fields) + extension(track.path)

        destination = os.path.join(parent(track.path), name)
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


def retag_album(album, mapping):
    """Uses information from a mapping to update the tags of a given Album

    Changes the tags of an Album and all contained tracks based on
    a mapping (eg. dict). Mappings not found in the track's supported
    fields will raise a NotImplementedError exception.

    """
    for name, field in mapping.items():
        if name in album.supported_fields() or name == 'tracks':
            setattr(album, name, field)
        else:
            raise NotImplementedError("Unsupported field: {}".format(field))

    for track in album:
        retag_track(track, mapping)


def retag_track(track, mapping):
    """Uses information from a mapping to update the tags of a given Track

    Changes the tags of a Track based on a mapping (eg. dict). Mappings
    not found in the track's supported fields will raise a
    NotImplementedError exception.
    """
    for name, field in mapping.items():
        if name in track.supported_fields():
            setattr(track, name, field)
        else:
            raise NotImplementedError("Unsupported field: {}".format(field))


def missing_fields(target):
    """Determines the missing fields in an Album or Track"""
    return [x for x in target.supported_fields() if not getattr(target, x)]
