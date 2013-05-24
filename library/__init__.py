"""r3tagger.library

The library provides some utility functions

Provides Functions:
    extension(path:str)
    Returns the file extension from a given path or filename

    parent(path:str, levels=1:int)
    Return the parent file the given levels above the given path

    filename(path:str)
    Return the file name from a given path. Includes file extension.

Provides Classes:
    TimedSemaphore(delay:int, value:int)
    Semaphore with a delay prior to releasing a lock

    LimitRequests(key:hashable, delay:int, value:int)
    Decorator to restrict the number of times that a function
    can be invoked in a given time.
"""

import os
from threading import _Semaphore, Timer


class TimedSemaphore(_Semaphore):
    """Semaphore with a delay prior to releasing
    An example use would be limiting the number of requests made to some
    restricted remote API in a given time period. For example the
    musicbrainz API restricts queries to one per second, and this is
    used as the default for this class.

    (http://musicbrainz.org/doc/XML_Web_Service/Rate_Limiting)
    """
    def __init__(self, delay=1, *args, **kwargs):
        """Adds a new argument, delay, the number of seconds to delay
        prior to releasing the lock. See threading._Semaphore  and
        threading.Semaphore (factory function) for additional help.
        """
        self._delay = delay
        super(TimedSemaphore, self).__init__(*args, **kwargs)

    def release(self, *args, **kwargs):
        release_func = super(TimedSemaphore, self).release
        release_timer = Timer(self._delay,
                              release_func,
                              args=args,
                              kwargs=kwargs)
        release_timer.start()


class LimitRequests(object):
    """Decorator to limit the rate of a functions invokation
    The limit may be shared across any number of functions by
    providing a similar key, which must be hashable. The function
    is limited to 'value' number of invokations in a given time
    period defined by 'delay'. The default value for both 'delay'
    and 'value' is 1.

    If all decorated functions in a module are to share a limit, the
    global __name__ variable would make a good key in most cases.
    """
    _locks = {}

    def __init__(self, key, delay=1, value=1):
        self._key = key
        self._lock = self._share_lock(key, delay, value)

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self._lock:
                return func(*args, **kwargs)

        return wrapper

    @classmethod
    def _share_lock(cls, key, delay, value):
        lock = cls._locks.get(key)

        if not lock:
            new_lock = TimedSemaphore(delay, value)
            cls._locks[key] = new_lock
            return new_lock

        return lock


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
