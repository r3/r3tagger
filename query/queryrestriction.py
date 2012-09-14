import threading


class SemaphoreDecorator(object):
    """Semaphore decorator

    Limits accessing code to 100 requests per second by default. A new limit
    (total executions per second) may be set using the set_limit method or
    as an optional argument in instantiation. All decorated functions will
    be subject to the same restriction and will block for half a second before
    continuing to process new requests.

    Note that changing the limit of the semaphore will remove all acquisitions
    """
    _access_count = 0
    limit = 100
    _lock = threading.BoundedSemaphore(limit)

    def __init__(self, limit=None):
        if limit is not None:
            self.set_limit(limit)

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self._lock:
                func(*args, **kwargs)

        return wrapper

    @classmethod
    def _create_semaphore(cls):
        cls._lock = threading.BoundedSemaphore(cls.limit)

    @classmethod
    def set_limit(cls, limit):
        cls.limit = limit
        cls._create_semaphore()
