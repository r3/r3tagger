"""Tests the Album object"""
import Musicbrainz
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
        mock_MusicbrainzQueries.inject_mocks(Musicbrainz)

        # Remove delay on functions
        Musicbrainz.Backoff._set_delay(0)

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
        try:
            return first.getId() == second.getId()
        except AttributeError:
            for a, b in zip(first, second):
                if a.getId() != b.getId():
                    return False

            return True

    # Test Methods
    def test__find_artist(self, responses):
        response = responses['_find_artist:Nirvana']
        assert response == Musicbrainz._find_artist(ARTIST)
        #pass

    def test__find_release_group(self, responses):
        response = responses['_find_release_group:Nevermind']
        assert response == Musicbrainz._find_release_group(ALBUM)
        #pass

    def test__find_title(self, responses):
        response = responses['_find_title:Smells Like Teen Spirit']
        assert self.same_mb_object(response, Musicbrainz._find_title(SONG))

    def test__find_title_artists(self, responses):
        response = responses['_find_title_artists:Smells Like Teen Spirit']
        assert response == Musicbrainz._find_title_artists(SONG)
        #pass

    def test__find_title_releases(self, responses):
        response = responses['_find_title_releases:Smells Like Teen Spirit']
        assert response == Musicbrainz._find_title_releases(SONG)
        #pass

    def test__lookup_artist_id(self, responses):
        ident = ('http://musicbrainz.org/artist/'
                 '5b11f4ce-a62d-471e-81fc-a69a8278c7da')
        assert self.same_mb_object(responses[ident],
                Musicbrainz._lookup_artist_id(ident))

    def test__lookup_release_group_id(self, responses):
        ident = ('http://musicbrainz.org/release-group/'
                 '1b022e01-4da6-387b-8658-8678046e4cef')
        assert self.same_mb_object(responses[ident],
                Musicbrainz._lookup_release_group_id(ident))

    def test__lookup_release_id(self, responses):
        ident = ('http://musicbrainz.org/release/'
                 'b52a8f31-b5ab-34e9-92f4-f5b7110220f0')
        assert self.same_mb_object(responses[ident],
            Musicbrainz._lookup_release_id(ident))

    def test_get_album(self, responses):
        response = responses['get_album:Nevermind']
        assert self.same_mb_object(response,
                Musicbrainz.get_album(ALBUM).next())

    def test_get_artist(self, responses):
        response = responses['get_artist:Nirvana']
        assert self.same_mb_object(response,
                Musicbrainz.get_artist(ARTIST).next())

    #def test_album_tags(self, artist, responses):
        #TODO: Build artist funcarg and complete

    #def test_artist_releases(self, artist, responses)
        #TODO: Build artist funcarg and complete
