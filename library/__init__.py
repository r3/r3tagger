"""r3tagger.library

The library provides some utility functions

Provides Functions:
    extension(path:str)
    Returns the file extension from a given path or filename

    parent(path:str, levels=1:int)
    Return the parent file the given levels above the given path

    filename(path:str)
    Return the file name from a given path. Includes file extension.
"""

import os
from threading import _Semaphore, Timer


class TimedSemaphore(_Semaphore):
    def __init__(self, delay=1, *args, **kwargs):
        """Semaphore with a delay prior to releasing
        Adds a new argument, delay, the number of seconds to delay
        prior to releasing the lock. An example use would be limiting
        the number of requests made to some restricted remote API in
        a given time period. For example the musicbrainz API restricts
        queries to one per second, and this is used as the default
        for this class.

        (http://musicbrainz.org/doc/XML_Web_Service/Rate_Limiting)
        """
        self.delay = delay
        super(TimedSemaphore, self).__init__(*args, **kwargs)

    def release(self, *args, **kwargs):
        release_func = super(TimedSemaphore, self).release
        release_timer = Timer(self.delay,
                              release_func,
                              args=args,
                              kwargs=kwargs)
        release_timer.start()


def extension(path):
    """Returns file extension

        extension('/path/to/file.ext') => '.ext'
    """
    return os.path.splitext(path)[-1]


def parent(path, levels=1):
    """Returns the parent in the path

        parent('/path/to/file.ext') => '/path/to'

    Allows the specification of the number of levels to strip away

        parent('/path/to/file.ext', 2) => '/path'
    """
    #TODO: Account for resolving relative paths:
    #      ./ryan => /home/ryan

    if path.endswith(os.path.sep):
        result = os.path.dirname(path)
    else:
        result = path

    for level in range(levels):
        result = os.path.dirname(result)

    return result


def filename(path):
    """Returns the filename from a path

        filename('/path/to/file.ext') => 'file.ext'
    """
    return os.path.split(path)[-1]
