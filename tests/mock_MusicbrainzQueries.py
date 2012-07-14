import shelve
mb_responses = shelve.open('mock_MusicbrainzQueries.shelve')


def getArtists(*args, **kwargs):
    """Query: 'Nirvana'"""
    return mb_responses['Nirvana Ids']


def getReleaseGroups(*args, **kwargs):
    """Query: 'Nevermind'"""
    return mb_responses['Nevermind Release Groups']


def getTracks(*args, **kwargs):
    """Query: 'Smells Like Teen Spirit'"""
    return mb_responses['Teen Spirit Tracks']


def getReleaseGroupById(*args, **kwargs):
    """Lookup of ID for 'Nevermind' (release group)
    http://musicbrainz.org/release-group/1b022e01-4da6-387b-8658-8678046e4cef
    """
    return mb_responses['Nevermind Id']


def getArtistById(*args, **kwargs):
    """Lookup of ID for 'Nirvana'
    http://musicbrainz.org/artist/5b11f4ce-a62d-471e-81fc-a69a8278c7da
    """
    return mb_responses['Nirvana Id']


def getReleaseById(*args, **kwargs):
    """Lookup ID for 'Nevermind' (release)
    http://musicbrainz.org/release/b52a8f31-b5ab-34e9-92f4-f5b7110220f0
    """
    return mb_responses['Nevermind Release Id']


def inject_mocks(module):
    """Injects mock functions into musicbrainz library"""
    assert module.__name__ == 'musicbrainz'

    funcs = {'getArtists': getArtists,
             'getReleaseGroups': getReleaseGroups,
             'getTracks': getTracks,
             'getReleaseGroupById': getReleaseGroupById,
             'getArtistById': getArtistById,
             'getReleaseById': getReleaseById}

    for name, func in funcs.items():
        setattr(module.ws.Query, name, func)


def disconnect():
    mb_responses.close()
