import logging
logging.basicConfig(filename='musicbrainz.log', level=logging.WARNING)

from datetime import datetime, timedelta

import musicbrainz2.webservice as ws
import musicbrainz2.model as m

from Backoff import Backoff
DELAY = 5  # Seconds between query to API

debug = datetime.now()
x = timedelta(0)


def ding(name):
    global debug
    now = datetime.now()
    logging.warning("TIMING: {} (since last request) from {}".format(now - debug, name))
    debug = now


# === ID Finding ===
@Backoff(DELAY)
def _find_artist(artist):
    """Returns iterable of Artist Ids"""
    try:
        query = ws.Query()
        filt = ws.ArtistFilter(name=artist)

        logging.info("Query (getArtists) - {}".format(datetime.now()))
        ding('_find_artist')
        results = query.getArtists(filt)
    except ws.WebServiceError, e:
        if '503' in e:
            logging.debug('Error 503: Too many requests')
            return _find_artist(artist)
        else:
            logging.error('Error: {}'.format(e))

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
        logging.info("Query (getReleaseGroups) - {}".format(datetime.now()))
        ding('_find_release_group')
        results = query.getReleaseGroups(filt)
    except ws.WebServiceError, e:
        if '503' in e:
            logging.debug('Error 503: Too many requests')
            return _find_release_group(title)
        else:
            logging.error('Error: {}'.format(e))

    return [x.getReleaseGroup().getId() for x in results]


# TODO: Unused so far. Untested.
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

        logging.info("Query (getTrack) - {}".format(datetime.now()))
        ding('_find_title')
        results = query.getTracks(filt)
    except ws.WebServiceError, e:
        if '503' in e:
            logging.debug('Error 503: Too many requests')
            return _find_title_releases(title)
        else:
            logging.error('Error: {}'.format(e))

    return [x.getTrack() for x in results]


# TODO: See _find_title above
def _find_title_releases(title):
    """Function for interpreting title based searches as releases"""
    results = _find_title(title)
    return [x.getReleases()[0].getId() for x in results]


# TODO: See _find_title above
def _find_title_artists(title):
    """Function for interpreting title based searches as artists"""
    results = _find_title(title)
    return [x.getArtist().getId() for x in results]


# === Look-ups of IDs ===
@Backoff(DELAY)
def _lookup_release_group_id(ident):
    """Returns musicbrainz releaseGroup object"""
    try:
        query = ws.Query()
        filt = ws.ReleaseGroupIncludes(artist=True, releases=True)

        logging.info("Query (getReleaseGroupById) - {}".format(datetime.now()))
        ding('_lookup_release_group_id')
        return query.getReleaseGroupById(ident, filt)
    except ws.WebServiceError, e:
        if '503' in e:
            logging.debug('Error 503: Too many requests')
            return _lookup_release_group_id(ident)
        else:
            logging.error('Error: {}'.format(e))


@Backoff(DELAY)
def _lookup_artist_id(ident):
    """Returns musicbrainz Artist object"""
    try:
        query = ws.Query()
        filt = ws.ArtistIncludes(
                releases=(m.Release.TYPE_OFFICIAL, m.Release.TYPE_ALBUM),
                tags=True, releaseGroups=True)

        logging.info("Query (getArtistById) - {}".format(datetime.now()))
        ding('_lookup_artist_id')
        return query.getArtistById(ident, filt)
    except ws.WebServiceError, e:
        if '503' in e:
            logging.debug('Error 503: Too many requests')
            return _lookup_artist_id(ident)
        else:
            logging.error('Error: {}'.format(e))


@Backoff(DELAY)
def _lookup_release_id(ident):
    """Returns musicbrainz Release object"""
    try:
        query = ws.Query()
        filt = ws.ReleaseIncludes(artist=True, tracks=True,
                releaseEvents=True)

        logging.info("Query (getReleaseById) - {}".format(datetime.now()))
        ding('_lookup_release_id')
        return query.getReleaseById(ident, filt)
    except ws.WebServiceError, e:
        if '503' in e:
            logging.debug('Error 503: Too many requests')
            return _lookup_release_id(ident)
        else:
            logging.error('Error: {}'.format(e))


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

    # TODO: I'm not happy with this algorithm, it feels weak
    # Supplying every release in a release group before trying the next
    # release sounds like a bad idea. Improvements?
    for release_group_id in idents:
        release_group = _lookup_release_group_id(release_group_id)
        if not release_group:
            logging.debug("ID: '{}' returned no releaseGroup object".format(
                release_group_id))
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


def artist_releases(artist):
    """Given a musicbrainz artist object, retrieve album releases
        Returns a generator of musicbrainz release objects sorted by
        the most likely in descending order

    """
    return (_lookup_release_id(x.getId()) for x in artist.getReleases())
