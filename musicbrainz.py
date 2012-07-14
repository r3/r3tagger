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
        Returns a generator of musicbrainz artist objects sorted by
        the most likely in descending order

        Note: queries with 'artist' are not currently supported
              as Lucene searches in _find_release_group aren't
              working.
    """
    if artist:
        # TODO: Fix Lucene searching in _find_release_group
        raise NotImplementedError("Lucene searches not implemented")
        idents = _find_release_group(title, artist)
    else:
        idents = _find_release_group(title)

    for release_group_id in idents:
        release_group = _lookup_release_group_id(release_group_id)
        for release in release_group.getReleases():
            yield _lookup_release_id(release.getId())


def get_artist(name):
    """Retrieve musicbrainz artist object from name
        Returns a generator of musicbrainz artist objects sorted by
        the most likely in descending order
    """
    idents = _find_artist(name)

    for artist_id in idents:
        yield _lookup_artist_id(artist_id)


# === Query resultant objects ===
def album_tags(album):
    """Collects tags for an album
        Returns a dictionary with the following fields:
        tracks, artist, year, title
    """
    results = {}

    results['tracks'] = [x.getTitle() for x in album.getTracks()]
    results['artist'] = album.getArtist().getName()
    results['year'] = album.getEarliestReleaseDate().split('-')[0]
    results['title'] = album.getTitle()

    return results


def artist_release(artist):
    """Given a musicbrainz artist object, retrieve album releases
        Returns a generator of musicbrainz release objects sorted by
        the most likely in descending order

    """
    return (_lookup_release_id(x.getId()) for x in artist.getReleases())
