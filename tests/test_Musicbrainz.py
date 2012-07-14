"""Tests the Album object"""
import musicbrainz
import mock_MusicbrainzQueries
import shelve

RESPONSES = 'MusicbrainzResponses.shelve'
SONG = 'Smells Like Teen Spirit'
ARTIST = 'Nirvana'
ALBUM = 'Nevermind'


class TestReadAlbum(object):
    """Tests the Album object"""

    # Setup/teardown methods as well as dependency injection
    def setup_responses(self):
        # Inject mock musicbrainz
        mock_MusicbrainzQueries.inject_mocks(musicbrainz)

        # Remove delay on functions
        musicbrainz.Backoff._set_delay(0)

        return shelve.open(RESPONSES)

    def teardown_responses(self, responses):
        # Disconnect Mock
        mock_MusicbrainzQueries.disconnect()

        responses.close()

    def pytest_funcarg__responses(self, request):
        """Dependency Injection: responses"""
        return request.cached_setup(self.setup_responses,
                self.teardown_responses, scope='class')

    @staticmethod
    def same_mb_object(first, second):
        if hasattr(first, 'getId') and hasattr(second, 'getId'):
            return first.getId() == second.getId()
        else:
            try:
                for a, b in zip(first, second):
                    if a.getId() != b.getId():
                        print("{} differs from {}".format(a, b))
                        print("A:\n{}".format(a.__dict__.keys()))
                        print("A Tag: {}".format(a._id))
                        print('\n')
                        print("B:\n{}".format(b.__dict__.keys()))
                        print("B Tag: {}".format(b._id))
                        return False

                return True
            except TypeError:
                print("First:\n\ttype: {}".format(type(first)))
                print("Second:\n\ttype: {}".format(type(second)))

    # Test Methods
    def test__find_artist(self, responses):
        response = responses['_find_artist:Nirvana']
        assert response == musicbrainz._find_artist(ARTIST)
        #pass

    def test__find_release_group(self, responses):
        response = responses['_find_release_group:Nevermind']
        assert response == musicbrainz._find_release_group(ALBUM)
        #pass

    def test__find_title(self, responses):
        response = responses['_find_title:Smells Like Teen Spirit']
        assert self.same_mb_object(response, musicbrainz._find_title(SONG))

    def test__find_title_artists(self, responses):
        response = responses['_find_title_artists:Smells Like Teen Spirit']
        assert response == musicbrainz._find_title_artists(SONG)
        #pass

    def test__find_title_releases(self, responses):
        response = responses['_find_title_releases:Smells Like Teen Spirit']
        assert response == musicbrainz._find_title_releases(SONG)
        #pass

    def test__lookup_artist_id(self, responses):
        ident = ('http://musicbrainz.org/artist/'
                 '5b11f4ce-a62d-471e-81fc-a69a8278c7da')
        assert self.same_mb_object(responses[ident],
                musicbrainz._lookup_artist_id(ident))

    def test__lookup_release_group_id(self, responses):
        ident = ('http://musicbrainz.org/release-group/'
                 '1b022e01-4da6-387b-8658-8678046e4cef')
        assert self.same_mb_object(responses[ident],
                musicbrainz._lookup_release_group_id(ident))

    def test__lookup_release_id(self, responses):
        ident = ('http://musicbrainz.org/release/'
                 'b52a8f31-b5ab-34e9-92f4-f5b7110220f0')
        assert self.same_mb_object(responses[ident],
            musicbrainz._lookup_release_id(ident))

    def test_get_album(self, responses):
        response = responses['get_album:Nevermind']
        assert self.same_mb_object(response, musicbrainz.get_album(ALBUM))

    def test_get_artist(self, responses):
        response = responses['get_artist:Nirvana']
        assert self.same_mb_object(response, musicbrainz.get_artist(ARTIST))

    #def test_album_tags(self, artist, responses):
        #TODO: Build artist funcarg and complete

    #def test_artist_releases(self, artist, responses)
        #TODO: Build artist funcarg and complete
