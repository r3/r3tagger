"""r3tagger.query.Acoustid

Requires: Chromaprint (http://acoustid.org/chromaprint)

An interface for querying the Acoustid database for information based on a
track. Each supported music file can be given a fingerprint by chromaprint
(automatically handled by Track interface).

Provides Functions:
    get_releases(track:Track)
"""

import json
import urllib2

from r3tagger.model.Album import Album
from r3tagger.query import QueryError, Musicbrainz


API_KEY = 'Eqin71st'


def _build_results(url):
    """Translate an Acoustid response to a data structure

    Acoustid uses an HTTP interface and transmits in JSON by default, which
    this function will turn into a nested dictionary. The structure of the
    Acoustid result will depend on meta arguments used in the query.
    """
    response = urllib2.urlopen(url)
    result = json.loads(response.read())

    if result['status'] == 'ok':
        return result
    else:
        error = result['status']
        raise QueryError('Query failed: Acoustid: {}'.format(error))


def _build_query_url(track, *meta):
    """Produce a query url for the given track

    Allows a number of extra arguments which will be treated as Acoustid
    meta arguments. The following arguments are allowed:

        recordings, recordingids, releases, releaseids, releasegroups,
        releasegroupids, tracks, puids, compress, usermeta, sources

    For more info on meta arguments, see: http://acoustid.org/webservice
    """
    url = 'http://api.acoustid.org/v2/lookup?client={}'.format(API_KEY)

    option = '&{}={}'
    url += option.format('duration', int(track.length))
    url += option.format('fingerprint', track.fingerprint)

    if meta:
        options = '+'.join(meta)
        url += option.format('meta', options)

    return url


def get_releases(track):
    """Retrieve musicbrainz release info from a track by fingerprinting

    Produces an iterable of possible releases in Album format from a Track.
    Queries the AcoustID database by finding the given Track's musicbrainz
    release ID, and then querying musicbrainz for that release. Uses the
    resulting information to construct an Album object for comparison.
    """
    url = _build_query_url(track, 'releaseids')
    results = _build_results(url)
    print results
    for match in results['results']:
        for release in match['releases']:
            print(release)
            musicbrainz_album = Musicbrainz._lookup_release_id(release['id'])
            tags_dict = Musicbrainz.album_tags(musicbrainz_album)

            yield(Album(tags_dict))
