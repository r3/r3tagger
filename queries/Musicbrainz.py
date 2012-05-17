import musicbrainz2.webservice as ws
import musicbrainz2.model as m
import time

last_request = None


def backoff(wait=1):
    """Musicbrainz allows for one request per second, this spaces requests"""
    global last_request
    if last_request and (time.time() - last_request < 1):
        time.sleep(wait - int((time.time() - last_request)))
    last_request = time.time()


def find_artist_id(artist):
    """Lookup Artist ID based on name
       Yields results in a generator
    """
    query = ws.ArtistFilter(name=artist)

    try:
        backoff()
        collect = ws.Query().getArtists(query)
    except ws.WebServiceError, e:
        if '503' in e:
            find_artist_id(artist)

    for ident in collect:
        yield ident.getArtist().getId()


def find_album_id(title, artist=None):
    """Lookup Album IDs matching a name
       Allows for optional arguments:
       artistName = artist name
       title = album title
       A given non-keyword argument will be treated as the album
       title to search for. Generator will supply most likely matches
       and continue yielding possible matches until exhausted.
    """
    def find_release_group_id(args):
        def release_lookup():
            inc = ws.ReleaseGroupFilter(**args)
            q = ws.Query()

            try:
                backoff()
                return q.getReleaseGroups(inc)
            except ws.WebServiceError, e:
                if '503' in e:
                    return find_release_group_id(args)

        releases = [x.getReleaseGroup() for x in release_lookup()]
        for release in releases:
            yield release

    def lookup_release_group_id(ident):
        q = ws.Query()
        inc = ws.ReleaseGroupIncludes(artist=True, releases=True)

        try:
            backoff()
            return q.getReleaseGroupById(ident, inc)
        except ws.WebServiceError, e:
            if '503' in e:
                return lookup_release_group_id(ident)

    new_args = dict()
    if artist:
        new_args['artistName'] = unicode(artist)
    new_args['title'] = unicode(title)

    release_group_id = find_release_group_id(new_args)
    release_group = lookup_release_group_id(release_group_id.next().getId())
    for release in  release_group.getReleases():
        yield release.getId()


def lookup_artist_id(ident):
    """Query musicbrainz for artist information"""
    q = ws.Query()
    inc = ws.ArtistIncludes(releases=(m.Release.TYPE_ALBUM,
                                      m.Release.TYPE_OFFICIAL))
    try:
        backoff()
        return q.getArtistById(ident, inc)
    except ws.WebServiceError, e:
        if '503' in e:
            return lookup_artist_id(ident)


def lookup_album_id(ident):
    """Query musicbrainz for album information"""
    q = ws.Query()
    inc = ws.ReleaseIncludes(artist=True, tracks=True, releaseEvents=True)

    try:
        backoff()
        return q.getReleaseById(ident, inc)
    except ws.WebServiceError, e:
        if '503' in e:
            return lookup_album_id(ident)


def get_artist(artist):
    """Retrieve musicbrainz artist object from artist name"""
    for artist_ident in find_artist_id(artist):
        yield lookup_artist_id(artist_ident)


def get_album(title, artist=None):
    """Retrieve musicbrainz album object from album title
       If returned album is not desired, increment result for the next
       most likely candidate. Iterates over remaining candidates if requested.
    """
    if artist:
        ident = find_album_id(title, artist)
    else:
        ident = find_album_id(title)
    for album_id in ident:
        yield lookup_album_id(album_id)


def album_track_count(album):
    """Given a musicbrainz album object, determine the number of tracks
       Used in conjunction with get_album results
    """
    return len(album.getTracks())


def album_tracks(album):
    """Given a musicbrainz album object, retrieve track list
       Used in conjunction with get_album results
    """
    return [x.getTitle() for x in album.getTracks()]


def album_artist(album):
    """Given a msuicbrainz album object, retrieve artist
       Used in conjuction with get_album results
    """
    return album.getArtist().getName()


def album_year(album):
    """Given a musicbrainz album object, retrieve release date
       Used in conjunction with get_album results
    """
    date = album.getReleaseEvents()[0].getDate()
    return date.split('-')[0]


def artist_releases(artist):
    """Given a musicbrainz artist object, retrieve album releases
       Used in conjunction with get_artist results
    """
    for release in artist.getReleases():
        yield lookup_album_id(release.getId())


def query_album(album, tags):
    """Given a musicbrainz album object, retrieve it and query requested tags.
       Requested information will be returned in a dictionary keyed by tags
       argument. Track titles, if requested, will be returned in a tuple
       (mapped to 'track') and returned in the order that they appear on the
       album. No numbering will be present but can be derived from length.
    """

    mapping = dict(artist='album.getArtist().getName()',
                   album='album.getTitle()',
                   year='album.getEarliestReleaseDate()')
    res = dict()

    for tag in tags:
        if tag in mapping:
            res[tag] = eval(mapping[tag])
        elif tag in ('title', 'track'):
            res[tag] = album_tracks(album)
        else:
            raise Exception("Requested bad information ({})".format(tag))

    return res
