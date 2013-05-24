import shelve
import os

import pytest
import musicbrainz2.webservice as ws
import musicbrainz2.model as m

from mocks import MusicbrainzQueries
from r3tagger.query import musicbrainz, QueryError

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
            if hasattr(first, 'getArtist') and hasattr(second, 'getArtist'):
                first_artists = [x.getArtist() for x in first]
                second_artists = [x.getArtist() for x in second]
                items = zip(first_artists, second_artists)
            else:
                items = zip(first, second)

            for a, b in items:
                if a.getId() != b.getId():
                    return False

            return True

    def test_setup_mock_hack(self, responses):
        """If MUSICBRAINZ_MOCK is set, inject the mock"""
        if os.getenv('MUSICBRAINZ_MOCK', '').lower() not in (None,
                                                             'false', 'no'):
            # reticulating_splines()
            MusicbrainzQueries.inject_mock(musicbrainz)
            MusicbrainzQueries.link_shelve(responses)
            musicbrainz.DELAY = 0

    # Test Methods
    def test__find_artist(self):
        for ident in musicbrainz._find_artist(ARTIST):
            assert ident.startswith('http://musicbrainz.org/artist/')

    def test__find_release_group(self):
        for ident in musicbrainz._find_release_group(ALBUM):
            assert ident.startswith('http://musicbrainz.org/release-group/')

    def test__find_track(self):
        for ident in musicbrainz._find_track(SONG):
            assert isinstance(ident, m.Track)

    def test__find_track_artists(self):
        for ident in musicbrainz._find_track_artists(SONG):
            assert ident.startswith('http://musicbrainz.org/artist/')

    def test__find_track_releases(self):
        for ident in musicbrainz._find_track_releases(SONG):
            assert ident.startswith('http://musicbrainz.org/release/')

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
        release = musicbrainz._lookup_release_id(ident)
        assert self.same_mb_object(responses[ident], release)

    def test_get_album(self, responses):
        response = responses['get_album:Nevermind']
        assert response.match(musicbrainz.get_album(ALBUM).next()) == 1

    def test_get_album_with_artist(self, responses):
        response = responses['get_album:Nevermind']
        mb_response = musicbrainz.get_album(ALBUM, ARTIST).next()
        assert response.match(mb_response) == 1

    def test_get_artist(self, responses):
        response = responses['get_artist:Nirvana']
        assert self.same_mb_object(response,
                                   musicbrainz.get_artist(ARTIST).next())

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

        assert musicbrainz.album_tags(album) == response

    def test_artist_releases(self, album, responses):
        # Get an artist object
        ident = ('http://musicbrainz.org/artist/'
                 '5b11f4ce-a62d-471e-81fc-a69a8278c7da')
        artist = responses[ident]

        release = musicbrainz.artist_releases(artist).next().getId()
        assert release.startswith('http://musicbrainz.org/release/')


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
        MusicbrainzQueries.raise_error(ws.WebServiceError)

    def test_all_methods_fail(self):
        methods = ('_find_artist', '_find_release_group', '_find_track',
                   '_lookup_artist_id', '_lookup_release_group_id',
                   '_lookup_release_id')

        if os.getenv('MUSICBRAINZ_MOCK', '').lower() not in (None,
                                                             'false', 'no'):
            for method in methods:
                with pytest.raises(QueryError):
                    getattr(musicbrainz, method)('dummy_arg')
