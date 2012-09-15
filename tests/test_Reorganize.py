import shutil
import tempfile
from os import path

from r3tagger import controller
from r3tagger.model.album import Album
from r3tagger.library import reorganize, parent


class TestReorganize():
    collection_root = None

    def _assert_exists(self, target, collection_root):
        if isinstance(target, Album):
            collection = (target,)
        else:
            collection = target

        for album in collection:
            album_name = '{} - {}'.format(album.date, album.album)
            complete_path = path.join(collection_root, album_name)

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
        shutil.rmtree(new_root)

    def pytest_funcarg__new_root(self, request):
        return request(self.setup_new_root, self.teardown_new_root,
                       scope='function')

    def setup_album(self):
        tempdir = tempfile.mkdtemp()

        orig_path = 'test_songs/album'
        dest_path = path.join(tempdir, 'album')

        shutil.copytree(orig_path, dest_path)

        return controller.build_albums(dest_path, False).next()

    def teardown_album(self, album):
        root = path.dirname(album.path)
        shutil.rmtree(root)

    def pytest_funcarg__album(self, request):
        return request.cached_setup(self.setup_album,
                                    self.teardown_album,
                                    scope='function')

    def setup_collection(self):
        tempdir = tempfile.mkdtemp()

        orig_path = 'test_songs/album'
        collection_root = path.join(tempdir, 'collection')
        TestReorganize.collection_root = collection_root
        dest_path = path.join(collection_root, 'album')

        shutil.copytree(orig_path, dest_path)

        return controller.build_albums('test_songs/album')

    def teardown_collection(self, collection):
        shutil.rmtree(TestReorganize.collection_root)

    def pytest_funcarg__collection(self, request):
        return request.cached_setup(self.setup_collection,
                                    self.teardown_collection,
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
        collection_root = TestReorganize.collection_root

        reorganize.reorganize_and_rename_collection(
            collection_root,
            "{artist}/{date} - {album}/{tracknumber} - {title}")

        self._assert_exists(collection, collection_root)

    def test_rename_and_reorganize_collection_with_album(self, album):
        reorganize.reorganize_and_rename_collection(
            album.path,
            "{artist}/{date} - {album}/{tracknumber} - {title}",
            include_only=album)

        self._assert_exists(album, parent(album.path))

#if __name__ == '__main__':
    #instance = TestReorganize()
    #album = instance.setup_album()
    #reorganize.reorganize_and_rename_collection(album.path,
                                                #include_only=album)
