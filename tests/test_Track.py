import tempfile
import shutil
import os
import pytest

from r3tagger.model import Track


class TestWriteTrack(object):
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
            TestWriteTrack.dir = tempfile.mkdtemp()

            orig_path = os.path.join('test_songs', TestWriteTrack.filename)
            dest_path = os.path.join(TestWriteTrack.dir, TestWriteTrack.filename)

            shutil.copyfile(orig_path, dest_path)
            TestWriteTrack.song = dest_path
            return Track.Track(dest_path)

        def pytest_funcarg__song(self, request):
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
            assert song.artist == u'altArtist'
            song()

        def test_write_album(self, song):
            song.album = 'altAlbum'
            assert song.album == u'altAlbum'
            song()

        def test_write_title(self, song):
            song.title = 'altTitle'
            assert song.title == u'altTitle'
            song()

        def test_write_tracknumber(self, song):
            song.tracknumber = '00'
            assert song.tracknumber == u'00'
            song()

        def test_write_date(self, song):
            song.date = '1999'
            assert song.date == u'1999'
            song()

        def test_write_genre(self, song):
            song.genre = 'altGenre'
            assert song.genre == u'altGenre'
            song()

    class TestReadBundle:
        # Setup 'song' funcarg and setup/teardown
        def setup_song(self):
            """Setup: Open edited dummy song"""
            return Track.Track(TestWriteTrack.song)

        def teardown_song(self, song):
            """Teardown: Delete directory containing dummy file"""
            shutil.rmtree(TestWriteTrack.dir)

        def pytest_funcarg__song(self, request):
            """Dependency Injection: Track"""
            return request.cached_setup(self.setup_song,
                    self.teardown_song,
                    scope='class')

        # Read tests
        def test_to_string(self, song):
            assert str(song) == 'altTitle'

        def test_read_altered_artist(self, song):
            assert song.artist == u'altArtist'

        def test_read_altered_album(self, song):
            assert song.album == u'altAlbum'

        def test_read_altered_title(self, song):
            assert song.title == u'altTitle'

        def test_read_altered_tracknumber(self, song):
            assert song.tracknumber == u'00'

        def test_read_altered_date(self, song):
            assert song.date == u'1999'

        def test_read_altered_genre(self, song):
            assert song.genre == u'altGenre'

        def test_read_length(self, song):
            def near(reference, test_num, bounds=0.05):
                return (reference - bounds) < test_num < (reference + bounds)

            #0.7886621315192743 is the length given in manual tests
            assert near(song.length, 0.788)


class TestAcoustid(object):
    """Provides a test suite for ensuring that fingerprints are properly
       generated from an mp3 file. Asserts that a newly made fingerprint
       matches one pregenerated and stored in a file (it's a long string)

       Fingerpring: test_songs/PublicDomainFingerprint.txt
       Musicbrainz Page for song:
        http://musicbrainz.org/recording/f037f7cf-7454-4b55-9dfe-06e8ea641e40
    """

    dir = None
    song = None
    filename = 'PublicDomainSong.mp3'

    def setup_song(self):
        TestAcoustid.dir = tempfile.mkdtemp()

        orig_path = os.path.join('test_songs', TestAcoustid.filename)
        dest_path = os.path.join(TestAcoustid.dir, TestAcoustid.filename)

        shutil.copyfile(orig_path, dest_path)
        TestAcoustid.song = dest_path
        return Track.Track(dest_path)

    def teardown_song(self, song):
        shutil.rmtree(TestAcoustid.dir)

    def pytest_funcarg__song(self, request):
        return request.cached_setup(self.setup_song,
                scope='class')

    def test_acoustid(self, song):
        with open('test_songs/PublicDomainFingerprint.txt') as fingerprint:
            assert ''.join(fingerprint) == song.fingerprint


class TestFailures(object):
    """Provides a test suite for ensuring that fingerprints are properly
       generated from an mp3 file. Asserts that a newly made fingerprint
       matches one pregenerated and stored in a file (it's a long string)

       Fingerpring: test_songs/PublicDomainFingerprint.txt
       Musicbrainz Page for song:
        http://musicbrainz.org/recording/f037f7cf-7454-4b55-9dfe-06e8ea641e40
    """

    dir = None
    song = None
    filename = 'PublicDomainSong.mp3'

    def setup_song(self):
        TestAcoustid.dir = tempfile.mkdtemp()

        orig_path = os.path.join('test_songs', TestAcoustid.filename)
        dest_path = os.path.join(TestAcoustid.dir, TestAcoustid.filename)

        shutil.copyfile(orig_path, dest_path)
        TestAcoustid.song = dest_path
        return Track.Track(dest_path)

    def teardown_song(self, song):
        """Teardown: Delete directory containing dummy file"""
        shutil.rmtree(TestAcoustid.dir)

    def pytest_funcarg__song(self, request):
        return request.cached_setup(self.setup_song,
                scope='class')

    def test_unsupported_file(self):
        path = os.path.join('test_songs', 'Unsupported.file')
        with pytest.raises(NotImplementedError):
            Track.Track(path)

    def test_missing_attrib(self, song):
        with pytest.raises(AttributeError):
            getattr(song, 'asnbrlAlkhasf')
