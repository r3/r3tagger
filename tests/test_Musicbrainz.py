import shelve
import os

import pytest
from musicbrainz2.webservice import WebServiceError

from mocks import MusicbrainzQueries
from r3tagger.query import Musicbrainz, QueryError

RESPONSES = 'mocks/MusicbrainzResponses.shelve'
SONG = 'Smells Like Teen Spirit'
ARTIST = 'Nirvana'
ALBUM = 'Nevermind'


class TestReadMusicbrainz(object):
    """Tests the Album object"""

    # Setup/teardown methods as well as dependency injection
    def setup_responses(self):
        return shelve.open(RESPONSES)

    def teardown_responses(self, responses):
        responses.close()

    def pytest_funcarg__responses(self, request):
        """Dependency Injection: responses"""
        return request.cached_setup(self.setup_responses,
                self.teardown_responses, scope='class')

    def setup_shelf(self):
        shelf = shelve.open('./mocks/SomeAlbumInstance.shelve')
        return shelf

    def teardown_shelf(self, shelf):
        shelf.close()

    def pytest_funcarg__shelf(self, request):
        return request.cached_setup(self.setup_shelf,
                self.teardown_shelf, scope='class')

    def pytest_funcarg__album(self, request):
        response = {'artist': u"Nirvana",
                    'album': u"Nevermind",
                    'date': u"1991",
                    'tracks': [u'Smells Like Teen Spirit',
                               u'In Bloom',
                               u'Come as You Are',
                               u'Breed',
                               u'Lithium',
                               u'Polly',
                               u'Territorial Pissings',
                               u'Drain You',
                               u'Lounge Act',
                               u'Stay Away',
                               u'On a Plain',
                               u'Something in the Way / Endless, Nameless']
                    }
        return response

    @staticmethod
    def same_mb_object(first, second):
        try:
            return first.getId() == second.getId()
        except AttributeError:
            for a, b in zip(first, second):
                if a.getId() != b.getId():
                    return False

            return True

    def test_setup_mock_hack(self, responses):
        """If MUSICBRAINZ_MOCK is set, inject the mock"""
        if os.getenv('MUSICBRAINZ_MOCK', '').lower() not in (None,
                                                             'false', 'no'):
            # reticulating_splines()
            MusicbrainzQueries.inject_mock(Musicbrainz)
            MusicbrainzQueries.link_shelve(responses)
            Musicbrainz.Backoff._set_delay(0)

    # Test Methods
    def test__find_artist(self, responses):
        response = responses['_find_artist:Nirvana']
        assert response == Musicbrainz._find_artist(ARTIST)

    def test__find_release_group(self, responses):
        response = responses['_find_release_group:Nevermind']
        assert response == Musicbrainz._find_release_group(ALBUM)

    def test__find_track(self, responses):
        response = responses['_find_title:Smells Like Teen Spirit']
        assert self.same_mb_object(response, Musicbrainz._find_track(SONG))

    def test__find_track_artists(self, responses):
        response = responses['_find_title_artists:Smells Like Teen Spirit']
        assert response == Musicbrainz._find_track_artists(SONG)

    def test__find_track_releases(self, responses):
        response = responses['_find_title_releases:Smells Like Teen Spirit']
        assert response == Musicbrainz._find_track_releases(SONG)

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

    def test_get_album_with_artist(self, responses):
        response = responses['get_album:Nevermind']
        assert self.same_mb_object(response,
                Musicbrainz.get_album(ALBUM, ARTIST).next())

    def test_get_artist(self, responses):
        response = responses['get_artist:Nirvana']
        assert self.same_mb_object(response,
                Musicbrainz.get_artist(ARTIST).next())

    def test_album_tags(self, album, responses):
        # Get a release object
        ident = ('http://musicbrainz.org/release/'
                 'b52a8f31-b5ab-34e9-92f4-f5b7110220f0')
        album = responses[ident]

        response = {'artist': u"Nirvana",
                    'album': u"Nevermind",
                    'date': u"1991",
                    'tracks': [u'Smells Like Teen Spirit',
                               u'In Bloom',
                               u'Come as You Are',
                               u'Breed',
                               u'Lithium',
                               u'Polly',
                               u'Territorial Pissings',
                               u'Drain You',
                               u'Lounge Act',
                               u'Stay Away',
                               u'On a Plain',
                               u'Something in the Way / Endless, Nameless']
                    }

        assert Musicbrainz.album_tags(album) == response

    def test_artist_releases(self, album, responses):
        # Get an release object
        ident = ('http://musicbrainz.org/release/'
                 'b52a8f31-b5ab-34e9-92f4-f5b7110220f0')
        album = responses[ident]

        # Get an artist object
        ident = ('http://musicbrainz.org/artist/'
                 '5b11f4ce-a62d-471e-81fc-a69a8278c7da')
        artist = responses[ident]

        first = Musicbrainz.artist_releases(artist).next()
        assert TestReadMusicbrainz.same_mb_object(first, album)


class TestMusicbrainzFails():
    def setup_responses(self):
        return shelve.open(RESPONSES)

    def teardown_responses(self, responses):
        responses.close()

    def pytest_funcarg__responses(self, request):
        """Dependency Injection: responses"""
        return request.cached_setup(self.setup_responses,
                self.teardown_responses, scope='class')

    def test_setup_mock_hack(self, responses):
        MusicbrainzQueries.raise_error(WebServiceError)

    def test_all_methods_fail(self):
        methods = ('_find_artist', '_find_release_group', '_find_track',
                   '_lookup_artist_id', '_lookup_release_group_id',
                   '_lookup_release_id')

        for method in methods:
            with pytest.raises(QueryError):
                getattr(Musicbrainz, method)('dummy_arg')
