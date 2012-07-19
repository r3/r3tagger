"""r3tagger.query.Acoustid

Provides Functions:
    lookup_track(track:Track)
    Given a track, return the information from Acoustid
"""


def lookup_track(track, api_key='Eqin71st'):
    """Query AcoustID for the given track's fingerprint"""
    url = 'http://api.acoustid.org/v2/lookup?client={}'.format(api_key)
    option = '{key}={value}'

    url += option.format('duration', track.length)
    url += option.format('fingerprint', track.fingerprint)
