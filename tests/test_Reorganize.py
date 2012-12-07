import shutil
import tempfile
import re
from os import path

from r3tagger import controller
from r3tagger.model.album import Album
from r3tagger.library import reorganize


class TestReorganize():
    collection_root = None

    def _assert_exists(self, target, collection_root):
        if isinstance(target, Album):
            collection = (target,)
        else:
            collection = target

        for album in collection:
            artist_name = album.artist
            partial_path = path.join(collection_root, artist_name)
            album_name = '{} - {}'.format(album.date, album.album)
            complete_path = path.join(partial_path, album_name)

            assert path.isdir(complete_path)

            for track_number in range(1, 6):
                track_name = '{0} - {1:0>2} - SomeTrack{1:0>2}.ogg'.format(
                    album.artist,
                    track_number)
                track_path = path.join(complete_path, track_name)

                assert path.isfile(track_path)

    def setup_new_root(self):
        TestReorganize.collection_root = tempfile.mkdtemp()
        return None

    def teardown_new_root(self, new_root):
        #shutil.rmtree(new_root)
        pass

    def pytest_funcarg__new_root(self, request):
        return request(self.setup_new_root,
                       #self.teardown_new_root,
                       scope='function')

    def setup_album(self):
        tempdir = tempfile.mkdtemp()

        orig_path = 'test_songs/album'
        dest_path = path.join(tempdir, 'album')

        shutil.copytree(orig_path, dest_path)

        return controller.build_albums(dest_path, False).next()

    def teardown_album(self, album):
        tempdir = re.match(r'/tmp/[a-zA-Z0-9]+/', album.path)
        if tempdir and path.exists(tempdir.group()):
            #shutil.rmtree(tempdir.group())
            pass

    def pytest_funcarg__album(self, request):
        return request.cached_setup(self.setup_album,
                                    #self.teardown_album,
                                    scope='function')

    def setup_collection(self):
        tempdir = tempfile.mkdtemp()

        orig_path = 'test_songs/album/nested-album'
        dest_path = path.join(tempdir, 'album')
        shutil.copytree(orig_path, dest_path)
        TestReorganize.collection_root = tempdir

        return tempdir

    def teardown_collection(self, collection):
        #shutil.rmtree(TestReorganize.collection_root)
        pass

    def pytest_funcarg__collection(self, request):
        return request.cached_setup(self.setup_collection,
                                    #self.teardown_collection,
                                    scope='function')

    def test_rename_album_default_pattern(self, album):
        root = path.dirname(album.path)

        reorganize.rename_album(album)

        newpath = "{} - {}".format(album.date, album.album)
        album_path = path.join(root, newpath)

        assert album_path == album.path
        assert path.exists(album_path)

        for track in album:
            assert path.dirname(track.path) == album_path

    def test_rename_tracks_default_pattern(self, album):
        reorganize.rename_tracks(album)

        parent_path = path.dirname(album.tracks[0].path)
        pattern = path.join(parent_path,
                            'SomeArtist - {:0>2} - SomeTrack{:0>2}.ogg')
        track_paths = [pattern.format(x, x) for x in range(5, 0, -1)]

        for track_path, track in zip(track_paths, album):
            assert track.path == track_path
            assert path.exists(track.path)

    def test_rename_and_reorganize_collection(self, collection):
        albums = controller.build_albums(collection, True)
        reorganize.reorganize_and_rename_collection(collection)
        self._assert_exists(albums, collection)

    def test_rename_and_reorganize_collection_with_album(self, collection):
        album_path = path.join(collection, 'album')
        album = next(controller.build_albums(album_path))

        reorganize.reorganize_and_rename_collection(
            collection, include_only=album)

        self._assert_exists(album, collection)

    def test_move_album_explicit_destination(self, album):
        destination = tempfile.mkdtemp()
        folder_name = path.basename(album.path)
        album_path = path.join(destination, folder_name)
        reorganize.move_album(album, album_path)
        assert path.isdir(destination)
        assert path.isdir(album_path)
        assert album.path == album_path

        pattern = path.join(album_path, '{:0>2}.ogg')
        for track_path in [pattern.format(x, x) for x in range(5, 0, -1)]:
            assert path.isfile(track_path)

    def test_move_album_into_dir(self, album):
        destination = tempfile.mkdtemp()
        folder_name = path.basename(album.path)
        reorganize.move_album(album, destination)
        album_path = path.join(destination, folder_name)
        assert path.isdir(destination)
        assert path.isdir(album_path)
        assert album.path == album_path

        pattern = path.join(album_path, '{:0>2}.ogg')
        for track_path in [pattern.format(x, x) for x in range(5, 0, -1)]:
            assert path.isfile(track_path)

    def test_move_album_into_self_subdir(self, album):
        destination = path.join(album.path, 'subdir')
        reorganize.move_album(album, destination)
        assert path.isdir(destination)
        assert album.path == destination

        pattern = path.join(destination, '{:0>2}.ogg')
        for track_path in [pattern.format(x, x) for x in range(5, 0, -1)]:
            assert path.isfile(track_path)
            assert path.dirname(track_path) == destination
