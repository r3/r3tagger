import tempfile
import shutil
import os
import pytest

from r3tagger.model.track import Track


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
            dest_path = os.path.join(
                TestWriteTrack.dir, TestWriteTrack.filename)

            shutil.copyfile(orig_path, dest_path)
            TestWriteTrack.song = dest_path
            return Track(dest_path)

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

        def test_reset_tags(self, song):
            song.album = 'AnotherAlbum'
            assert song.album == 'AnotherAlbum'
            song.reset_tags()
            assert song.album == u'altAlbum'

    class TestReadBundle:
        # Setup 'song' funcarg and setup/teardown
        def setup_song(self):
            """Setup: Open edited dummy song"""
            return Track(TestWriteTrack.song)

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

        def test_length(self, song):
            assert round(song.length, 3) == 0.789

        def test_bitrate(self, song):
            assert song.bitrate == 160000

        def test_supported_fields(self, song):
            assert song.supported_fields() == ('artist', 'album', 'title',
                                               'tracknumber', 'date', 'genre')


class TestTrackFingerprint(object):
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
        TestTrackFingerprint.dir = tempfile.mkdtemp()

        orig_path = os.path.join('test_songs', TestTrackFingerprint.filename)
        dest_path = os.path.join(TestTrackFingerprint.dir,
                                 TestTrackFingerprint.filename)

        shutil.copyfile(orig_path, dest_path)
        TestTrackFingerprint.song = dest_path
        return Track(dest_path)

    def teardown_song(self, song):
        shutil.rmtree(TestTrackFingerprint.dir)

    def pytest_funcarg__song(self, request):
        return request.cached_setup(self.setup_song,
                                    scope='class')

    def test_acoustid(self, song):
        with open('test_songs/PublicDomainFingerprint.txt') as fingerprint:
            fp = ''.join(fingerprint).strip()
            assert fp == song.fingerprint


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
        #See below!
        TestFailures.dir = tempfile.mkdtemp()

        orig_path = os.path.join('test_songs', TestFailures.filename)
        dest_path = os.path.join(TestFailures.dir, TestFailures.filename)

        shutil.copyfile(orig_path, dest_path)
        TestFailures.song = dest_path
        return Track(dest_path)

    def teardown_song(self, song):
        """Teardown: Delete directory containing dummy file"""
        #TODO: Ugly. Get the path from the song!
        shutil.rmtree(TestFailures.dir)

    def pytest_funcarg__song(self, request):
        return request.cached_setup(self.setup_song,
                                    scope='class')

    def test_unsupported_file(self):
        path = os.path.join('test_songs', 'Unsupported.file')
        with pytest.raises(NotImplementedError):
            Track(path)

    def test_missing_attrib(self, song):
        with pytest.raises(AttributeError):
            getattr(song, 'asnbrlAlkhasf')


@pytest.fixture(scope='module')
def untagged_mp3_path(request):
    filename = 'untagged.mp3'
    temp_path = tempfile.mkdtemp()
    orig_path = os.path.join('test_songs', filename)
    dest_path = os.path.join(temp_path, filename)

    shutil.copyfile(orig_path, dest_path)

    def delete_tempfile():
        shutil.rmtree(temp_path)

    request.addfinalizer(delete_tempfile)
    return dest_path


def test_instantiate_untagged_mp3(untagged_mp3_path):
    Track(untagged_mp3_path)
