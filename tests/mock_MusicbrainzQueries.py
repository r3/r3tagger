import shelve
mb_responses = shelve.open('mock_MusicbrainzQueries.shelve')


class ws():
    class Query():
        def getArtists(self, *args, **kwargs):
            """Query: 'Nirvana'"""
            return mb_responses['Nirvana Id']

        def getReleaseGroups(self, *args, **kwargs):
            """Query: 'Nevermind'"""
            return mb_responses['Nevermind Release Groups']

        def getTracks(self, *args, **kwargs):
            """Query: 'Smells Like Teen Spirit'"""
            return mb_responses['Teen Spirit Tracks']

    class WebServiceError():
        def __init__(self, *args, **kwargs):
            pass

    def ArtistFilter(self, *args, **kwargs):
        return None

    def ReleaseGroupFilter(self, *args, **kwargs):
        return None

    def TrackFilter(self, *args, **kwargs):
        return None

    def ReleaseGroupIncludes(self, *args, **kwargs):
        return None

    def ArtistIncludes(self, *args, **kwargs):
        return None


class m():
    class Release():
        TYPE_OFFICIAL = 1
        TYPE_ALBUM = 2
