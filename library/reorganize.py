import os
import shutil
import ConfigParser

from r3tagger.library import parent, extension
from r3tagger import FileExistsError
from r3tagger.controller import set_album_path

# Config loading
parent_dir = parent(os.path.dirname(__file__))
config_file = os.path.join(parent_dir, 'r3tagger.cfg')
config = ConfigParser.RawConfigParser()
config.read(config_file)

THRESHOLD = config.get('Main', 'match-threshold')
TRACK_PATTERN = config.get('Main', 'track-pattern')
ALBUM_PATTERN = config.get('Main', 'album-pattern')


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

    try:
        # Try to iterate through target, if you can, it's an Album
        for track in target:
            rename_track(track, pattern)
    except TypeError:
        # If you can't iterate, it's a Track
        rename_track(target, pattern)


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

    set_album_path(album, destination)
