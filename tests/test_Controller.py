"""Tests the Controller object"""

import shelve
import shutil
import os
import tempfile
import Controller

#import mock_MusicbrainzQueries as queries


class TestCreateAlbum(object):
    """Tests the creation of an album from a path"""

    path = None

    # Setup/teardown methods as well as dependency injection
    def setup_path(self):
        """Setup: Creates a test album with 5 dummy songs on it"""
        tempdir = tempfile.mkdtemp()

        orig_path = 'test_songs/album'
        dest_path = os.path.join(tempdir, 'album')

        shutil.copytree(orig_path, dest_path)
        TestCreateAlbum.path = dest_path

        return dest_path

    def teardown_path(self, album):
        """Teardown: Destroys test album and cleans up temp files"""
        shutil.rmtree(TestCreateAlbum.path)

    def pytest_funcarg__path(self, request):
        """Dependency Injection: Album"""
        return request.cached_setup(self.setup_path, self.teardown_path,
                scope='class')

    def setup_controller(self):
        """Setup: Creates a test album with 5 dummy songs on it"""
        return Controller

    def pytest_funcarg__controller(self, request):
        """Dependency Injection: Album"""
        return request.cached_setup(self.setup_controller, scope='module')

    def test_single_album(self, path):
        persist_album = shelve.open('SomeAlbumInstance.shelve')['SomeAlbum']
        test_album = Controller.build_albums(path).next()
        assert persist_album.match(test_album) == 1.0
