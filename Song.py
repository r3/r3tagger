"""Song Class

Author: r3 (ryan.roler@gmail.com)
Date: 03.17.2012"""

class Song(object):
    """Path to a file and metadata that represents a song"""

    def __init__(
            self,
            path = None,
            artist = None,
            title = None,
            track_no = None,
            year = None,
            genre = None):
        
        self.path = path
        self.artist = artist
        self.title = title
        self.track_no = track_no
        self.year = year
        self.genre = genre
