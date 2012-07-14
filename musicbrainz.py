import musicbrainz2.webservice as ws
import musicbrainz2.model as m

from Backoff import Backoff
DELAY = 5  # Seconds between query to API


# === ID Finding ===
@Backoff(DELAY)
def _find_artist(artist):
    """Returns iterable of Artist Ids"""
    try:
        query = ws.Query()
        filt = ws.ArtistFilter(name=artist)

        results = query.getArtists(filt)
    except ws.WebServiceError, e:
        if '503' in e:
            _find_artist(artist)

    return [x.getArtist().getId() for x in results]


@Backoff(DELAY)
def _find_release_group(title, artist=None):
    """Returns iterable of releaseGroups"""
    if artist:
        # TODO: Figure out why my Lucene searches aren't working
        raise NotImplementedError("Lucene searches not implemented")
        pattern = '"{}" AND artist:"{}"'.format(title, artist)  # Lucene
    else:
        pattern = title

    filt = ws.ReleaseGroupFilter(pattern)

    try:
        query = ws.Query()
        results = query.getReleaseGroups(filt)
    except ws.WebServiceError, e:
        print("Error!")
        if '503' in e:
            return _find_release_group(title)

    return [x.getReleaseGroup().getId() for x in results]


@Backoff(DELAY)
def _find_title(title):
    """Returns iterable of Artist Ids
        Really should be called from either:
        _find_title_releases
        _find_title_artists
    """
    try:
        query = ws.Query()
        filt = ws.TrackFilter(title)

        results = query.getTracks(filt)
    except ws.WebServiceError, e:
        if '503' in e:
            _find_title_releases(title)

    return results


def _find_title_releases(title):
    """Function for interpreting title based searches as releases"""
    results = _find_title(title)
    return [x.getTrack().getReleases()[0].getId() for x in results]


def _find_title_artists(title):
    """Function for interpreting title based searches as artists"""
    results = _find_title(title)
    return [x.getTrack().getArtist().getId() for x in results]


# === Look-ups of IDs ===
@Backoff(DELAY)
def _lookup_release_group_id(ident):
    """Returns musicbrainz releaseGroup object"""
    try:
        query = ws.Query()
        filt = ws.ReleaseGroupIncludes(artist=True, releases=True)

        return query.getReleaseGroupById(ident, filt)
    except ws.WebServiceError, e:
        if '503' in e:
            return _lookup_release_group_id(ident)


@Backoff(DELAY)
def _lookup_artist_id(ident):
    """Returns musicbrainz Artist object"""
    try:
        query = ws.Query()
        filt = ws.ArtistIncludes(
                releases=(m.Release.TYPE_OFFICIAL, m.Release.TYPE_ALBUM),
                tags=True, releaseGroups=True)

        return query.getArtistById(ident, filt)
    except ws.WebServiceError, e:
        if '503' in e:
            return _lookup_artist_id(ident)


@Backoff(DELAY)
def _lookup_release_id(ident):
    """Returns musicbrainz Release object"""
    try:
        query = ws.Query()
        filt = ws.ReleaseIncludes(artist=True, tracks=True,
                releaseEvents=True)

        return query.getReleaseById(ident, filt)
    except ws.WebServiceError, e:
        if '503' in e:
            return _lookup_release_id(ident)


# === High level query interfaces ===

def get_album(title, artist=None):
    """Retrieve musicbrainz album object from album title
        If returned album is not desired, increment result for the next
        most likely candidate. Iterates over remaining candidates if requested.
    """
    if artist:
        idents = _find_release_group(title, artist)
    else:
        idents = _find_release_group(title)

    for release_group_id in idents:
        release_group = _lookup_release_group_id(release_group_id)
        for release in release_group.getReleases():
            yield _lookup_release_id(release.getId())


def get_artist(name):
    """Retrieve musicbrainz artist object from name
    Results will be an iterator of possible artists sorted in descending
    order by the likelyhood of the match
    """
    idents = _find_artist(name)

    for artist_id in idents:
        yield _lookup_artist_id(artist_id)


# === Query resultant objects ===
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
        yield _lookup_release_group_id(release.getId())


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
