"""Tests the Album object"""

import shutil
import os
import tempfile

from Song import Song
from Album import Album


class TestReadAlbum(object):
    """Tests the Album object"""

    path = None

    # Setup/teardown methods as well as dependency injection
    def setup_album(self):
        """Setup: Creates a test album with 5 dummy songs on it"""
        tempdir = tempfile.mkdtemp()

        orig_path = 'test_songs/album'
        dest_path = os.path.join(tempdir, 'album')

        shutil.copytree(orig_path, dest_path)
        TestReadAlbum.path = dest_path

        pattern = 'test_songs/album/{:0>2}.ogg'

        tracks = [Song(pattern.format(x)) for x in range(1, 6)]

        return Album(tracks)

    def teardown_album(self, album):
        """Teardown: Destroys test album and cleans up temp files"""
        shutil.rmtree(TestReadAlbum.path)

    def pytest_funcarg__album(self, request):
        """Dependency Injection: Album"""
        return request.cached_setup(self.setup_album, self.teardown_album,
                scope='class')

    # Test Methods
    def test_iterable(self, album):
        """Test album has five songs"""
        count = 0

        for song in album:
            count += 1

        assert count == 5

    def test_title(self, album):
        assert album.album == 'SomeAlbum'

    def test_artist(self, album):
        assert album.artist == 'SomeArtist'

    def test_date(self, album):
        assert album.date == '2012'

    def test_genre(self, album):
        assert album.genre == 'SomeGenre'

    def test_save_tracks(self, album):
        assert album() == None


class TestBuildFromDict(object):
    """Tests the Album object's ability to instantiate on a dict"""

    # Setup/teardown methods as well as dependency injection
    def setup_album(self):
        """Setup: Creates a test album with 5 dummy songs on it"""
        descriptor = dict()
        descriptor['album'] = 'SomeAlbum'
        descriptor['artist'] = 'SomeArtist'
        descriptor['date'] = '2012'
        descriptor['genre'] = 'SomeGenre'
        descriptor['tracks'] = ['01', '02', '03', '04', '05']
        return Album(descriptor)

    def pytest_funcarg__album(self, request):
        """Dependency Injection: Album"""
        return request.cached_setup(self.setup_album, scope='class')

    def test_title(self, album):
        assert album.album == 'SomeAlbum'

    def test_artist(self, album):
        assert album.artist == 'SomeArtist'

    def test_date(self, album):
        assert album.date == '2012'

    def test_genre(self, album):
        assert album.genre == 'SomeGenre'

    def test_tracks(self, album):
        assert album.tracks == ['01', '02', '03', '04', '05']


class TestAlbumMatching(object):
    """Tests the Album's ability to fuzzy match other Album instances"""

    # Setup/teardown methods as well as dependency injection
    def setup_matchingmock(self):
        """Setup: Creates a test album with 5 dummy songs on it"""
        descriptor = dict()
        descriptor['album'] = 'SomeAlbum'
        descriptor['artist'] = 'SomeArtist'
        descriptor['date'] = '2012'
        descriptor['genre'] = 'SomeGenre'
        descriptor['tracks'] = ['SomeTrack01', 'SomeTrack02', 'SomeTrack03',
                                'SomeTrack04', 'SomeTrack05']
        return Album(descriptor)

    def pytest_funcarg__matchingmock(self, request):
        """Dependency Injection: Album"""
        return request.cached_setup(self.setup_matchingmock, scope='class')

    def setup_similarmock(self):
        """Setup: Creates a test album with 5 dummy songs on it"""
        descriptor = dict()
        descriptor['album'] = 'SomeAlbum'
        descriptor['artist'] = 'SomeArtist'
        descriptor['date'] = '2012'
        descriptor['genre'] = 'SomeGenre'
        descriptor['tracks'] = ['SomeTrack01', 'SomeTrack02', 'SomeTrack03']
        return Album(descriptor)

    def pytest_funcarg__similarmock(self, request):
        """Dependency Injection: Album"""
        return request.cached_setup(self.setup_similarmock, scope='class')

    def setup_differentmock(self):
        """Setup: Creates a test album with 5 dummy songs on it"""
        descriptor = dict()
        descriptor['album'] = 'SomeOtherAlbum'
        descriptor['artist'] = 'SomeOtherArtist'
        descriptor['date'] = '1985'
        descriptor['genre'] = 'SomeOtherGenre'
        descriptor['tracks'] = ['SomeTrack01', 'SomeTrack02']
        return Album(descriptor)

    def pytest_funcarg__differentmock(self, request):
        """Dependency Injection: Album"""
        return request.cached_setup(self.setup_differentmock, scope='class')

    def setup_album(self):
        """Setup: Creates a test album with 5 dummy songs on it"""
        tempdir = tempfile.mkdtemp()

        orig_path = 'test_songs/album'
        dest_path = os.path.join(tempdir, 'album')

        shutil.copytree(orig_path, dest_path)
        TestReadAlbum.path = dest_path

        pattern = 'test_songs/album/{:0>2}.ogg'

        tracks = [Song(pattern.format(x)) for x in range(1, 6)]

        return Album(tracks)

    def teardown_album(self, album):
        """Teardown: Destroys test album and cleans up temp files"""
        shutil.rmtree(TestReadAlbum.path)

    def pytest_funcarg__album(self, request):
        """Dependency Injection: Album"""
        return request.cached_setup(self.setup_album, self.teardown_album,
                scope='class')

    def test_perfect_match(self, album, matchingmock):
        assert album.match(matchingmock) == 1.0

    def test_similar_match(self, album, similarmock):
        assert 0 < album.match(similarmock) < 1.0

    def test_no_match(self, album, differentmock):
        assert album.match(differentmock) == 0.0
