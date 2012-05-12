def lookup_artist(name):
    return {'artist': 'Robert Wilkins'}


def lookup_album(name, artist=None):
    if artist is None:
        return {'album': 'The Original Rolling Stone'}
    else:
        return {'album': 'The Original Rolling Stone',
                'artist': 'Robert Wilkins'}
