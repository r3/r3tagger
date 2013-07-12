"""Tests the Controller object"""

import shelve
import shutil
import os
import tempfile

import pytest

from r3tagger import controller
from r3tagger.model.album import Album


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
        return controller

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

    def test_fix_config_path_hack(self):
        controller.config_file = os.path.dirname(controller.__file__)

    def test_build_track_supported(self):
        track = controller.build_track('test_songs/PublicDomainSong.mp3')
        with open('test_songs/PublicDomainFingerprint.txt') as fingerprint:
            fp = ''.join(fingerprint).strip()
            assert fp == track.fingerprint

    def test_build_track_unsupported(self):
        with pytest.raises(NotImplementedError):
            controller.build_track('test_Controller.py')

    def test_build_track_missing(self):
        with pytest.raises(controller.NoFileFoundError):
            controller.build_track('.')

    def test_single_album(self, path, persist):
        test_album = controller.build_albums(path).next()
        assert persist.match(test_album) == 1.0

    def test_recursive_albums(self, path, persist):
        for album in controller.build_albums(path, True):
            assert persist.match(album) == 1.0

    def test_missing_album(self):
        with pytest.raises(controller.NoFileFoundError):
            controller.build_albums('.').next()

    def test_missing_fields_album(self, album):
        album.artist = None
        assert controller.missing_fields(album) == ['artist']

    def test_missing_fields_track(self, album):
        track = album.tracks[0]
        track.album = track.title = None

        assert sorted(controller.missing_fields(track)) == ['album', 'title']

    def test_get_fields_track(self, album):
        expected = {'album': u'SomeAlbum', 'title': u'SomeTrack05',
                    'artist': u'SomeArtist', 'date': u'2012',
                    'genre': u'SomeGenre', 'tracknumber': u'05'}
        track = album.tracks[0]
        for name, field in controller.get_fields(track).items():
            assert expected[name] == field

    def test_find_shared_tags_none(self, album, persist):
        album.tracks[0].artist = u'AnotherArtist'
        album.tracks[0].album = u'AnotherAlbum'
        album.tracks[0].genre = u'AnotherGenre'
        album.tracks[0].date = u'0'

        assert controller.find_shared_tags(album, persist) == {}

    def test_get_fields_album(self, album):
        expected = {'album': u'SomeAlbum', 'date': u'2012',
                    'genre': u'SomeGenre', 'artist': u'SomeArtist'}
        for name, field in controller.get_fields(album).items():
            assert expected[name] == field

    def test_find_shared_tags_partial(self, album, persist):
        expected = {'album': u'SomeAlbum', 'date': u'2012',
                    'genre': u'SomeGenre'}

        album.tracks[0].artist = u'AnotherArtist'

        assert controller.find_shared_tags(album, persist) == expected

    def test_album_from_tracks(self, album, persist):
        tracks = album.tracks
        new_album = controller.album_from_tracks(tracks)

        assert new_album.match(persist) == 1

    def test_album_from_tracks_with_name(self, album, persist):
        tracks = album.tracks
        new_album = controller.album_from_tracks(tracks, name="AnotherAlbum")

        assert 0.7 < new_album.match(persist) < 0.72


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

    def test_album(self, album):
        """Simply ensure that the test album is what I expect"""
        assert album.artist == 'SomeArtist'
        assert album.album == 'SomeAlbum'
        assert album.date == '2012'
        assert album.genre == 'SomeGenre'
        assert len(album.tracks) == 5

    def test_retag_album(self, album):
        tags = {'artist': 'NewArtist', 'album': 'NewAlbum',
                'date': '2013', 'genre': 'NewGenre'}

        controller.retag_album(album, tags)

        for name, tag in tags.items():
            assert getattr(album, name) == tag

            for track in album:
                assert getattr(track, name) == tag

    def test_retag_track(self, album):
        tags = {'artist': 'AnotherArtist', 'album': 'AnotherAlbum',
                'date': '2013', 'genre': 'AnotherGenre'}
        track = album.tracks[0]

        controller.retag_track(track, tags)

        for name, tag in tags.items():
            assert getattr(track, name) == tag

    def test_update_album(self, album):
        source = {'album': 'UpdatedAlbum',
                  'artist': 'UpdatedArtist',
                  'date': '1',
                  'genre': 'UpdatedGenre'}

        controller.update_album(album, Album(source))

        for name, field in source.items():
            assert getattr(album, name) == field

    def test_flush_changes_track(self, album):
        track = album[0]
        path = track.path
        artist = u'Foo'
        track.artist = artist
        controller.flush_changes(track)

        changed_track = controller.build_track(path)
        assert changed_track.artist == artist

    def test_flush_changes_album(self, album):
        path = album.path
        artist = u'Foo'
        controller.retag_album(album, {'artist': artist})
        controller.flush_changes(album)

        changed_album = controller.build_albums(path).next()
        assert changed_album.artist == artist

    def test_flush_changes_tracks(self, album):
        artist = u'Foo'
        tracks = []

        for track in album[0:3]:
            track.artist = artist

        paths = [track.path for track in tracks]
        controller.flush_changes(*tracks)

        for path in paths:
            changed_track = controller.build_track(path)
            assert changed_track.artist == artist


@pytest.fixture(scope='module')
def album(request):
    directory = 'nested-album'
    path = 'test_songs/album'
    temp_path = tempfile.mkdtemp()
    orig_path = os.path.join(path, directory)
    dest_path = os.path.join(temp_path, directory)

    shutil.copytree(orig_path, dest_path)

    def delete_tempfile():
        shutil.rmtree(temp_path)

    request.addfinalizer(delete_tempfile)
    return Album(dest_path)


@pytest.mark._parametrize("fields", {
    'artist': ['The Untempting', 'Disorienting Lag'],
    'title': ['Uncharted Love', 'Drawn Away'],
    'date': ['2013', '2000'],
    'genre': ['Classic Rock', 'Jazz']})
def test_tags_by_frequency(album, fields):
    for field, expected in fields.items():
        assert list(controller.tags_by_frequency(album, field)) == expected
