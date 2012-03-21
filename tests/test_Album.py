"""Tests the Album object"""

import shutil
import os
import tempfile
import Album
import Song

class TestReadAlbum(ProvidesAlbum):
    """Tests the Album object"""
    
    path = None

    # Setup/teardown methods as well as dependency injection
    def setup_album(self):
        """Setup: Creates a test album with 5 dummy songs on it"""
        tempdir = tempfile.mkdtemp()

        orig_path = 'test_songs/album'
        dest_path = os.path.join(tempdir, 'album')

        shutil.copytree(orig_path, dest_path)
        TestAlbum.path = dest_path

        return Album.Album([Song.Song(TestAlbum.path) for x in range(10)])

    def teardown_album(self):
        """Teardown: Destroys test album and cleans up temp files"""
        shutil.rmtree(TestAlbum.path)

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
        assert album.title == 'someAlbum'
        
    def test_artist(self, album):
        assert album.artist == 'someArtist'
        
    def test_date(self, album):
        assert album.date == '2012'
        
    def test_genre(self, album):
        assert album.genre == 'someGenre'
