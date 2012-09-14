import shutil
import tempfile
import os

from r3tagger import controller
from r3tagger.library import reorganize


class TestAlbumManipulation():
    def setup_album(self):
        tempdir = tempfile.mkdtemp()

        orig_path = 'test_songs/album'
        dest_path = os.path.join(tempdir, 'album')

        shutil.copytree(orig_path, dest_path)

        return controller.build_albums(dest_path, False).next()

    def teardown_album(self, album):
        root = os.path.dirname(album.path)
        shutil.rmtree(root)

    def pytest_funcarg__album(self, request):
        return request.cached_setup(self.setup_album, self.teardown_album,
                                    scope='function')

    def test_rename_album_default_pattern(self, album):
        root = os.path.dirname(album.path)

        reorganize.rename_album(album)

        newpath = "{} - {}".format(album.date, album.album)
        album_path = os.path.join(root, newpath)

        assert album_path == album.path
        assert os.path.exists(album_path)

        for track in album:
            assert os.path.dirname(track.path) == album_path

    def test_rename_tracks_default_pattern(self, album):
        reorganize.rename_tracks(album)

        path = os.path.dirname(album.tracks[0].path)
        pattern = os.path.join(path,
                               'SomeArtist - {:0>2} - SomeTrack{:0>2}.ogg')
        track_paths = [pattern.format(x, x) for x in range(5, 0, -1)]

        for path, track in zip(track_paths, album):
            assert track.path == path
            assert os.path.exists(track.path)
