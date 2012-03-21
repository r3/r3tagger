"""Tests the Song object"""

import tempfile
import shutil
import os
import Song

class TestReadSong(object):
    """Provides a test suite for reading pretagged songs

    artist == 'testArtist'
    title == 'testTitle'
    tracknumber == '01'
    date == '2012'
    genre == 'testGenre'

    These expected values coorespend with tagged_dummy.ogg file in
    the test_songs folder. As no changes are made to the file, it
    is not copied like in some other tests.
    """

    filename = 'tagged_dummy.ogg'

    # Setup copy of test file
    def setup_song(self):
        """Setup: Open tagged dummy song"""
        return Song.Song(os.path.join('test_songs', TestReadSong.filename))

    def pytest_funcarg__song(self, request):
        """Dependency Injection: Song"""
        return request.cached_setup(self.setup_song, scope='class')

    # Ensure file exists
    def test_song_has_path(self, song):
        assert hasattr(song, 'path')

    def test_file_exists(self, song):
        assert os.path.isfile(song.path)

    # Read tests
    def test_read_artist(self, song):
        assert song.artist == [u'testArtist']

    def test_read_album(self, song):
        assert song.album == [u'testAlbum']

    def test_read_title(self, song):
        assert song.title == [u'testTitle']

    def test_read_tracknumber(self, song):
        assert song.tracknumber == [u'01']

    def test_read_date(self, song):
        assert song.date == [u'2012']

    def test_read_genre(self, song):
        assert song.genre == [u'testGenre']


class TestWriteSong(object):
    """Provides a test suite for writing and reading fields

    artist == 'altArtist'
    title == 'altTitle'
    tracknumber == '00'
    date == '1999'
    genre == 'altGenre'

    These values are written to a temporary test file. The song is then closed
    and reopened. The tags will be checked to ensure that the changes were
    committed to the file.
    """

    dir = None
    song = None
    filename = 'dummy.ogg'

    class TestWriteBundle:
        # Setup 'song' funcarg and setup/teardown
        def setup_song(self):
            """Setup: Setup copy of dummy song"""
            TestWriteSong.dir = tempfile.mkdtemp()

            orig_path = os.path.join('test_songs', TestWriteSong.filename)
            dest_path = os.path.join(TestWriteSong.dir, TestWriteSong.filename)

            shutil.copyfile(orig_path, dest_path)
            TestWriteSong.song = dest_path
            return Song.Song(dest_path)

        def pytest_funcarg__song(self, request):
            """Dependency Injection: Song"""
            return request.cached_setup(self.setup_song,
                    scope='class')

        # Ensure file exists
        def test_song_has_path(self, song):
            assert hasattr(song, 'path')

        def test_file_exists(self, song):
            assert os.path.isfile(song.path)

        # Write tests
        def test_write_artist(self, song):
            song.artist = 'altArtist'
            assert song.artist == [u'altArtist']
            song()

        def test_write_album(self, song):
            song.album = 'altAlbum'
            assert song.album == [u'altAlbum']
            song()

        def test_write_title(self, song):
            song.title = 'altTitle'
            assert song.title == [u'altTitle']
            song()

        def test_write_tracknumber(self, song):
            song.tracknumber = '00'
            assert song.tracknumber == [u'00']
            song()

        def test_write_date(self, song):
            song.date = '1999'
            assert song.date == [u'1999']
            song()

        def test_write_genre(self, song):
            song.genre = 'altGenre'
            assert song.genre == [u'altGenre']
            song()

    class TestReadBundle:
        # Setup 'song' funcarg and setup/teardown
        def setup_song(self):
            """Setup: Open edited dummy song"""
            return Song.Song(TestWriteSong.song)

        def teardown_song(self, song):
            """Teardown: Delete directory containing dummy file"""
            shutil.rmtree(TestWriteSong.dir)

        def pytest_funcarg__song(self, request):
            """Dependency Injection: Song"""
            return request.cached_setup(self.setup_song,
                    self.teardown_song,
                    scope='class')

        # Read tests
        def test_read_altered_artist(self, song):
            assert song.artist == [u'altArtist']

        def test_read_altered_album(self, song):
            assert song.album == [u'altAlbum']

        def test_read_altered_title(self, song):
            assert song.title == [u'altTitle']

        def test_read_altered_tracknumber(self, song):
            assert song.tracknumber == [u'00']

        def test_read_altered_date(self, song):
            assert song.date == [u'1999']

        def test_read_altered_genre(self, song):
            assert song.genre == [u'altGenre']
