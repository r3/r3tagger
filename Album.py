"""Album Class

Author: r3 (ryan.roler@gmail.com)
Date: 03.17.2012"""

class Album(object):
    """Contains a list of songs and metadata that describes an album"""

    def __init__(self, artist=None, title=None, date=None, tracks=[None]):
        self.artist = artist
        self.title = title
        self.date = date
        self.tracks = tracks
        
    def _find_shared_tags(self):
        """Determines the fields that are shared between each of the Album's
        songs. Stored as sets in a dict keyed on the field name:
        
        dict(artist=
        """
        
        tracker = dict()

        def add_fields_from_song(song):
            for field in ('artist', 'title', 'date', 'tracks'):
                tracker.setdefault(field, set()).add(getatter(song, field))
        
        for song in self.tracks:
            add_fields_from_song(song)
            
        def is_shared(field_set):
            return len(field_set) == 1
            
        return {field_name : field.pop() for field_name, field in tracker}
