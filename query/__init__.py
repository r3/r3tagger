"""r3tagger.query

Contains the query interfaces to be used in the r3tagger as well as some
helper classes in this file

Provides Classes:
    QueryError
    General error to pass when queries fail

    Retry
    Decorater used to attempt to invoke the decorated function a number
    of times on the given error. Good for faulty network connections or
    accidentally making too many queries and getting a 503 from musicbrainz!
"""


import musicbrainz2.webservice as ws


class QueryError(ws.WebServiceError):
    pass


class Retry(object):
    def __init__(self, error, attempts=3):
        self.error = error
        self.attempts = attempts

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            for attempt in range(self.attempts):
                try:
                    return func(*args, **kwargs)
                except self.error, e:
                    pass

            raise QueryError("Query failed: {}".format(e))

        return wrapper
