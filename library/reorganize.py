import os
import shutil
import ConfigParser

from r3tagger import controller
from r3tagger import FileExistsError
from r3tagger.model.track import Track
from r3tagger.library import parent, extension

# Config loading
parent_dir = parent(os.path.dirname(__file__))
config_file = os.path.join(parent_dir, 'r3tagger.cfg')
config = ConfigParser.RawConfigParser()
config.read(config_file)

TRACK_PATTERN = config.get('Main', 'track-pattern')
ALBUM_PATTERN = config.get('Main', 'album-pattern')
COLLECTION_ROOT = config.get('Main', 'collection-root')
ORGANIZATION_PATTERN = config.get('Main', 'organization-pattern')


def rename_tracks(target, pattern=None):
    """Correct the file name of a Track to reflect tags and a given pattern

    Either Albums or Tracks are acceptable arguments to pass.

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

    if isinstance(target, Track):
        rename_track(target, pattern)
    else:
        for track in target:
            rename_track(track, pattern)


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

    controller.set_album_path(album, destination)


def reorganize_and_rename_collection(collection_root=None,
                                     organization_pattern=None,
                                     album_pattern=None,
                                     track_pattern=None):
    if not organization_pattern:
        organization_pattern = ORGANIZATION_PATTERN

    if not collection_root:
        collection_root = COLLECTION_ROOT

    if not album_pattern:
        album_pattern = ALBUM_PATTERN

    if not track_pattern:
        track_pattern = TRACK_PATTERN

    for album in controller.build_albums(collection_root, recursive=True):
        folder = os.path.basename(album.path)
        destination = os.path.join(collection_root, folder)
        shutil.move(album.path, destination)
        controller.set_album_path(album, destination)

        rename_album(album, album_pattern)
        rename_tracks(album, track_pattern)
