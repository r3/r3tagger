mb_responses = None
ERROR = None


def getArtists(*args, **kwargs):
    """Query: 'Nirvana'"""
    if ERROR:
        raise(ERROR)

    return mb_responses['Nirvana Ids']


def getReleaseGroups(*args, **kwargs):
    """Query: 'Nevermind'"""
    if ERROR:
        raise(ERROR)

    return mb_responses['Nevermind Release Groups']


def getTracks(*args, **kwargs):
    """Query: 'Smells Like Teen Spirit'"""
    if ERROR:
        raise(ERROR)

    return mb_responses['Teen Spirit Tracks']


def getReleaseGroupById(*args, **kwargs):
    """Lookup of ID for 'Nevermind' (release group)
    http://musicbrainz.org/release-group/1b022e01-4da6-387b-8658-8678046e4cef
    """
    if ERROR:
        raise(ERROR)

    return mb_responses['Nevermind Id']


def getArtistById(*args, **kwargs):
    """Lookup of ID for 'Nirvana'
    http://musicbrainz.org/artist/5b11f4ce-a62d-471e-81fc-a69a8278c7da
    """
    if ERROR:
        raise(ERROR)

    return mb_responses['Nirvana Id']


def getReleaseById(*args, **kwargs):
    """Lookup ID for 'Nevermind' (release)
    http://musicbrainz.org/release/b52a8f31-b5ab-34e9-92f4-f5b7110220f0
    """
    if ERROR:
        raise(ERROR)

    publicdomainsong_release_id = '80460fff-5cbb-430e-92d1-765e50a02317'

    if publicdomainsong_release_id in args:
        return mb_responses['publicdomain_release_id']
    else:
        return mb_responses['Nevermind Release Id']


def inject_mock(module):
    """Call FIRST"""
    funcs = {'getArtists': getArtists,
             'getReleaseGroups': getReleaseGroups,
             'getTracks': getTracks,
             'getReleaseGroupById': getReleaseGroupById,
             'getArtistById': getArtistById,
             'getReleaseById': getReleaseById}

    for name, func in funcs.items():
        setattr(module.ws.Query, name, func)


def link_shelve(shelve):
    """Call SECOND"""
    global mb_responses
    mb_responses = shelve


def raise_error(error):
    """Want errors? Let me know what kind"""
    global ERROR
    ERROR = error("Error created by mock for testing purposes.")
