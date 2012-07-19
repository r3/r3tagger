import os
import shelve

from mocks import MusicbrainzQueries
from mocks import AcoustidQueries

from r3tagger.query import Acoustid
from r3tagger.model.Track import Track


class TestAcoustid():
    def pytest_funcarg__track(self, request):
        return Track('test_songs/PublicDomainSong.mp3')

    def setup_expected(self):
        expected_responses = shelve.open('mocks/AcoustidResponses.shelve')
        return expected_responses

    def teardown_expected(self, expected):
        expected.close()

    def pytest_funcarg__expected(self, request):
        return request.cached_setup(self.setup_expected,
                self.teardown_expected, scope='class')

    def setup_mb(self):
        mb_responses = shelve.open('mocks/MusicbrainzResponses.shelve')
        return mb_responses

    def teardown_mb(self, mb):
        mb.close()

    def pytest_funcarg__mb(self, request):
        return request.cached_setup(self.setup_mb,
                self.teardown_mb, scope='class')

    #def test_inject_mocks_hack(self, expected, mb):
        #if os.getenv('MUSICBRAINZ_MOCK', '').lower() not in (None,
                #'false', 'no'):
            #MusicbrainzQueries.inject_mock(Acoustid.Musicbrainz)
            #MusicbrainzQueries.link_shelve(mb)
        #if os.getenv('ACOUSTID_MOCK', '').lower() not in (None,
                #'false', 'no'):
            #AcoustidQueries.inject_mock(Acoustid)
            #AcoustidQueries.link_shelve(expected)

    def test__build_results(self, track, expected):
        url = Acoustid._build_query_url(track)
        results = Acoustid._build_results(url)
        assert results == expected['_build_results']

    def test_get_releases(self, track, expected):
        result = Acoustid.get_releases(track)
        album = result.next()
        print album.__dict__
        print expected['get_releases'].__dict__
        assert expected['get_releases'].match(album) == 1
