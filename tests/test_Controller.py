"""Tests the Controller object"""

import shelve
import shutil
import os
import tempfile

import pytest

from r3tagger import Controller


class TestCreateAlbum(object):
    """Tests the creation of an album from a path"""

    path = None
    persist_album = None

    # Setup/teardown methods as well as dependency injection
    def setup_path(self):
        """Setup: Creates a test album with 5 dummy songs on it"""
        tempdir = tempfile.mkdtemp()

        orig_path = 'test_songs/album'
        dest_path = os.path.join(tempdir, 'album')

        shutil.copytree(orig_path, dest_path)
        TestCreateAlbum.path = dest_path

        return dest_path

    def teardown_path(self, request):
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

    def setup_persist(self):
        """Setup: Creates a test album with 5 dummy songs on it
        Constructed from pickeled data
        """
        tempdir = tempfile.mkdtemp()

        orig_path = 'mocks/SomeAlbumInstance.shelve'
        dest_path = os.path.join(tempdir, os.path.dirname(orig_path))

        shutil.copyfile(orig_path, dest_path)
        TestCreateAlbum.persist_album = dest_path

        return shelve.open(dest_path)['SomeAlbum']

    def teardown_persist(self, request):
        """Teardown: Destroys test album and cleans up temp files"""
        os.remove(TestCreateAlbum.persist_album)

    def pytest_funcarg__persist(self, request):
        """Dependency Injection: Album"""
        return request.cached_setup(self.setup_persist, self.teardown_persist,
                scope='class')

    def test_build_track_supported(self):
        track = Controller.build_track('test_songs/PublicDomainSong.mp3')
        with open('test_songs/PublicDomainFingerprint.txt') as fingerprint:
            assert ''.join(fingerprint) == track.fingerprint

    def test_build_track_unsupported(self):
        with pytest.raises(NotImplementedError):
            Controller.build_track('test_Controller.py')

    def test_build_track_missing(self):
        with pytest.raises(Controller.NoFileFoundError):
            Controller.build_track('.')

    def test_single_album(self, path, persist):
        test_album = Controller.build_albums(path).next()
        assert persist.match(test_album) == 1.0

    def test_recursive_albums(self, path, persist):
        for album in Controller.build_albums(path, True):
            assert persist.match(album) == 1.0

    def test_missing_album(self):
        with pytest.raises(Controller.NoFileFoundError):
            Controller.build_albums('.').next()


class TestAlbumManipulation():
    def setup_album(self):
        tempdir = tempfile.mkdtemp()

        orig_path = 'test_songs/album'
        dest_path = os.path.join(tempdir, 'album')

        shutil.copytree(orig_path, dest_path)

        return Controller.build_albums(dest_path, False).next()

    def teardown_album(self, album):
        root = os.path.dirname(album.path)
        shutil.rmtree(root)

    def pytest_funcarg__album(self, request):
        return request.cached_setup(self.setup_album, self.teardown_album,
                scope='function')

    def test_album(self, album):
        """Simply ensure that the test album is what I expect"""
        assert album.artist == 'SomeArtist'
        assert album.album == 'SomeAlbum'
        assert album.date == '2012'
        assert album.genre == 'SomeGenre'
        assert len(album.tracks) == 5

    def test_rename_album_default_pattern(self, album):
        root = os.path.dirname(album.path)

        Controller.rename_album(album)

        newpath = "{} - {}".format(album.date, album.album)
        album_path = os.path.join(root, newpath)

        assert album_path == album.path
        assert os.path.exists(album_path)

        for track in album:
            assert os.path.dirname(track.path) == album_path

    def test_rename_tracks_default_pattern(self, album):
        Controller.rename_tracks(album)

        path = os.path.dirname(album.tracks[0].path)
        pattern = os.path.join(path,
                'SomeArtist - {:0>2} - SomeTrack{:0>2}.ogg')
        track_paths = [pattern.format(x, x) for x in range(5, 0, -1)]

        for path, track in zip(track_paths, album):
            assert track.path == path
            assert os.path.exists(track.path)

    def test_retag_album(self, album):
        tags = {'artist': 'NewArtist', 'album': 'NewAlbum',
                'date': '2013', 'genre': 'NewGenre'}

        Controller.retag_album(album, tags)

        for name, tag in tags.items():
            assert getattr(album, name) == tag

            for track in album:
                assert getattr(track, name) == tag

    def test_retag_track(self, album):
        tags = {'artist': 'AnotherArtist', 'album': 'AnotherAlbum',
                'date': '2013', 'genre': 'AnotherGenre'}
        track = album.tracks[0]

        Controller.retag_track(track, tags)

        for name, tag in tags.items():
            assert getattr(track, name) == tag
