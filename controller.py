"""r3tagger.Controller

Handles the processing and construction of Albums and Tracks

Provided Functions:
    build_albums(album:Album, path:str)
    Produce iterables of Albums on path

    find_shared_tags(album:Album)
    Collects shard fields into a dict

    rename_album(album:Album)
    Renames an Album

    rename_tracks(target:Album|Track)
    Renames Track or Tracks in an Album

    retag_album(album:Album, mapping:dict)
    Retag an Album and contents based on a mapping

    retag_track(track:Track, mapping:dict)
    Retag a Track based on a mapping

    missing_fields(target:Album|Track)
    Returns list of fields that have missing tags

    update_album(target:Album, source:Album)
    Updates tags on target with those in source

    get_fields(target:Album|Track)
    Returns dictionary of the tags in target

    album_from_tracks(tracks:Tracks, name=None)
    Creates a container album with the given tracks and optional album name

    flush_changes(target:Albums|Tracks)
    Saves changes to any number of tracks and/or albums
"""

import os

from mutagen import File

from r3tagger.model.album import Album
from r3tagger.model.track import Track
from r3tagger.library import filename


# Classes
class NoFileFoundError(Exception):
    pass


# Functions
def set_album_path(album, path):
    """Change the path of an Album and each of its tracks"""
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
            return None

        album = Album(tracks)
        set_album_path(album, path)

        for field, shared_value in find_shared_tags(album).items():
            setattr(album, field, shared_value)

        return album

    if recursive is False:
        album = prep_album(os.listdir(path), path)

        if not album:
            raise NoFileFoundError("No supported tracks at {}".format(path))

        yield album

    else:
        for root, _, files in os.walk(path):
            album = prep_album(files, root)

            if not album:
                continue

            yield album


def find_shared_tags(*albums):
    """Finds field shared by all tracks on a given album
    Returns a dictionary mapping of fields to shared values.
    """
    try:
        sample_track = albums[0][0]
    except IndexError:
        return None

    def is_shared(field, albums):
        result = set()
        for album in albums:
            for track in album:
                result.add(getattr(track, field))

        return len(result) == 1

    album = albums[0]
    result = {}
    for field in sample_track.supported_fields():
        if is_shared(field, albums):
            result[field] = getattr(album.tracks[0], field)

    return result


def retag_album(album, mapping):
    """Uses information from a mapping to update the tags of a given Album

    Changes the tags of an Album and all contained tracks based on
    a mapping (eg. dict). Mappings not found in the track's supported
    fields will raise a NotImplementedError exception.

    """
    for name, field in mapping.items():
        if name in album.supported_fields():
            setattr(album, name, field)
        elif name == 'tracks':
            for track in album:
                retag_track(track, get_fields(mapping))

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

    track()  # Saves updates to disk


def missing_fields(target):
    """Determines the missing fields in an Album or Track"""
    return [x for x in target.supported_fields() if not getattr(target, x)]


def update_album(target, source):
    """Copy fields from source to target

    Supports all of the target's supported fields, and tracks. Each of these
    supported fields will be read from the source and written to the target.
    """
    # Grab supported fields
    supported = source.supported_fields()
    source_map = {field: getattr(source, field) for field in supported}

    # Grab tags that exist
    if hasattr(source, 'tracks') and source.tracks:
        source_map['tracks'] = source.tracks

    retag_album(target, source_map)


def get_fields(target):
    """Returns a mapping of the fields in the target Album or Track

    Mapping will use the target's supported fields, if they exist.
    If there is no supported_fields method, the target will be taken
    as a title and returned as such.
    """
    if hasattr(target, 'supported_fields'):
        supported = target.supported_fields()
        return {field: getattr(target, field) for field in supported}
    else:
        return {'title': target}


def album_from_tracks(tracks, name=None):
    """Creates a container album for the given tracks

    Accepts an optional name argument which will be used as the container
    album's album title (album.name). All fields aside from tracks (and name,
    if given) will be empty strings.
    """
    args = {'tracks': tracks}

    if name is not None:
        args['album'] = name

    return Album(args)


def flush_changes(*tracks_and_albums):
    """Flushes the changes made to given tracks and/or albums to disk

    Accepts any number of Track and/or Album objects
    """
    for item in tracks_and_albums:
        if isinstance(item, Album):
            for track in item:
                track()

        else:
            item()
