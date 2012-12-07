import os
import shutil
import tempfile
import ConfigParser

from r3tagger import controller, FileExistsError
from r3tagger.model.album import Album
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
# TODO: Move to config file
ARTIST_PATTERN = '{artist}'


def rename_tracks(target, pattern=TRACK_PATTERN):
    """Correct the file name of a Track to reflect tags and a given pattern

    Either Albums or Tracks are acceptable arguments to pass.

    A pattern may be passed as an argument, but rename_tracks will use the
    configuration files to select one.

    Pattern Example: '{artist} - {tracknumber} - {title}'
    """
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


def move_album(album, destination):
    """Move an Album to destination

    If the destination exists and is a file, FileExistsError will be raised.
    If the destination exists and is a folder, album will be placed inside
    of the folder. If the album is moving into a subpath of the existing path,
    the tracks will be moved (ie collection/artist -> collection/artist/album).
    """
    if os.path.isdir(destination):
        album_folder = os.path.basename(album.path)
        destination_path = os.path.join(destination, album_folder)
    elif os.path.exists(destination):
        raise FileExistsError(("File {} cannot be moved to destination:" +
                               "{} (Already Exists)").format(album.path,
                                                             destination))
    else:
        destination_path = destination

    if album.path in destination_path:
        if not os.path.isdir(destination_path):
            os.mkdir(destination_path)

        for track in [x.path for x in album]:
            shutil.move(track, destination_path)
    else:
        shutil.move(album.path, destination)

    controller.set_album_path(album, destination_path)


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


def reorganize_and_rename_collection(collection_root=COLLECTION_ROOT,
                                     organization_pattern=ORGANIZATION_PATTERN,
                                     album_pattern=ALBUM_PATTERN,
                                     track_pattern=TRACK_PATTERN,
                                     artist_pattern=ARTIST_PATTERN,
                                     include_only=None):

    if include_only:
        if isinstance(include_only, Album):
            collection = (include_only,)
        else:
            collection = include_only
    else:
        collection = controller.build_albums(collection_root, recursive=True)

    for album in collection:
        orig_path = album.path

        tempdir = tempfile.mkdtemp()
        dest_dir = os.path.join(tempdir, os.path.basename(album.path))
        shutil.copytree(album.path, dest_dir)
        controller.set_album_path(album, dest_dir)
        dest_path = tempdir

        for index, catagory in enumerate(organization_pattern.split('/')):
            if catagory == 'ARTIST':
                dest_path = _name_to_pattern(
                    album, dest_path, artist_pattern)
            elif catagory == 'ALBUM':
                dest_path = _name_to_pattern(
                    album, dest_path, album_pattern)
            elif catagory == 'TRACK':
                rename_tracks(album, track_pattern)

            if index == 0:
                root_path = dest_path

        #shutil.rmtree(orig_path)
        shutil.move(root_path, collection_root)
        shutil.rmtree(tempdir)


def _name_to_pattern(album, dest_dir, pattern):
    name = pattern.format(**controller.get_fields(album))
    dest = os.path.join(dest_dir, name)
    move_album(album, dest)
    return dest
