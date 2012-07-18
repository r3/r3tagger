"""r3tagger.query.Musicbrainz

Handles queries directed at the Musicbrainz database. Acts as a more
friendly interface than the required musicbrainz2, and provides the
expected methods of a query:

Provided Functions:
    get_album(title:str, artist=None:str)
    Provides an iterator of musicbrainz2 releases  #TODO: Make these Albums!
    Currently, the artist parameter is not functional.

    get_artist(artist:str)
    Provides an iterator of musicbrainz2 artists  #TODO: Make a model!

    album_tags(album:musicbrainz2.Release)
    Provides a dict of fields from a release.

    artist_releases(artist:musicbrainz2.Artist)
    Provide an iterator of musicbrainz2  releases.  #TODO: Make these Albums!
"""

import logging
logging.basicConfig(filename='musicbrainz.log', level=logging.DEBUG)

import musicbrainz2.webservice as ws
import musicbrainz2.model as m

from r3tagger.query import Retry
from r3tagger.library.Backoff import Backoff
DELAY = 5  # Seconds between query to API


# === ID Finding ===
@Retry(ws.WebServiceError)
@Backoff(DELAY)
def _find_artist(artist):
    """Returns iterable of Artist Ids"""
    query = ws.Query()
    filt = ws.ArtistFilter(name=artist)

    results = query.getArtists(filt)

    return [x.getArtist().getId() for x in results]


@Retry(ws.WebServiceError)
@Backoff(DELAY)
def _find_release_group(title, artist=None):
    """Returns iterable of releaseGroups"""
    if artist:
        pattern = '"{}" AND artist:"{}"'.format(title, artist)
    else:
        pattern = title

    try:
        filt = ws.ReleaseGroupFilter(query=pattern)
        query = ws.Query()
        results = query.getReleaseGroups(filt)
    except ws.WebServiceError, e:
        if '503' in e:
            logging.debug('Error 503: Too many requests')
            return _find_release_group(title)
        else:
            logging.error('Other Error: {}'.format(e))

    return [x.getReleaseGroup().getId() for x in results]


@Retry(ws.WebServiceError)
@Backoff(DELAY)
def _find_track(track):
    """Returns iterable of Artist Ids
    Really should be called from either:
    _find_track_releases
    _find_track_artists
    """
    try:
        query = ws.Query()
        filt = ws.TrackFilter(track)
        results = query.getTracks(filt)
    except ws.WebServiceError, e:
        if '503' in e:
            logging.debug('Error 503: Too many requests')
            return _find_track_releases(track)
        else:
            logging.error('Other Error: {}'.format(e))

    return [x.getTrack() for x in results]


def _find_track_releases(track):
    """Function for interpreting track based searches as releases"""
    results = _find_track(track)
    return [x.getReleases()[0].getId() for x in results]


def _find_track_artists(track):
    """Function for interpreting track based searches as artists"""
    results = _find_track(track)
    return [x.getArtist().getId() for x in results]


# === Look-ups of IDs ===
@Retry(ws.WebServiceError)
@Backoff(DELAY)
def _lookup_release_group_id(ident):
    """Returns musicbrainz releaseGroup object"""
    try:
        query = ws.Query()
        filt = ws.ReleaseGroupIncludes(artist=True, releases=True)

        return query.getReleaseGroupById(ident, filt)
    except ws.WebServiceError, e:
        if '503' in e:
            logging.debug('Error 503: Too many requests')
            return _lookup_release_group_id(ident)
        else:
            logging.error('Other Error: {}'.format(e))


@Retry(ws.WebServiceError)
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
            logging.debug('Error 503: Too many requests')
            return _lookup_artist_id(ident)
        else:
            logging.error('Other Error: {}'.format(e))


@Retry(ws.WebServiceError)
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
            logging.debug('Error 503: Too many requests')
            return _lookup_release_id(ident)
        else:
            logging.error('Other Error: {}'.format(e))


# === High level query interfaces ===

def get_album(title, artist=None):
    """Retrieve musicbrainz album object from album title

    Returns a generator of musicbrainz artist objects sorted by
    the most likely in descending order
    """
    if artist:
        idents = _find_release_group(title, artist)
    else:
        idents = _find_release_group(title)

    # TODO: I'm not happy with this algorithm, it feels weak
    # Supplying every release in a release group before trying the next
    # release sounds like a bad idea. Improvements?
    for release_group_id in idents:
        release_group = _lookup_release_group_id(release_group_id)
        if not release_group:
            logging.error("ID: '{}' returned no releaseGroup object".format(
                release_group_id))
        for release in release_group.getReleases():
            yield _lookup_release_id(release.getId())


def get_artist(name):
    """Retrieve musicbrainz artist object from name

    Returns a generator of musicbrainz artist objects sorted by the most
    likely in descending order
    """
    idents = _find_artist(name)

    for artist_id in idents:
        yield _lookup_artist_id(artist_id)


# === Query resultant objects ===
def album_tags(album):
    """Collects tags for an album

    Returns a dictionary with the following fields:
    tracks, artist, date, album
    """
    results = {}

    results['tracks'] = [x.getTitle() for x in album.getTracks()]
    results['artist'] = album.getArtist().getName()
    results['date'] = album.getEarliestReleaseDate().split('-')[0]
    results['album'] = album.getTitle()

    return results


def artist_releases(artist):
    """Given a musicbrainz artist object, retrieve album releases

    Returns a generator of musicbrainz release objects sorted by
    the most likely in descending order
    """
    return (_lookup_release_id(x.getId()) for x in artist.getReleases())
