#!/usr/bin/env python
"""Backoff Decorator

https://github.com/r3

Author: Ryan Roler (ryan.roler@gmail.com)
Date: 07/13/2012
License: LGPL
Requires: Python 2 or 3

Description:
    Creates a 'Backoff' class to be used as a decorator for functions that
    require a delay between the resolutions of those functions. The delay
    can be blocking or nonblocking as designated by the decorator's second
    parameter.

    # blocking example:

        from backoff import Backoff

        @Backoff(seconds=5)
        def func_needing_delay():
            pass

    # non-blocking example:

        from backoff import Backoff

        @Backoff(5, blocking=False)
        def func_needing_delay():
            pass

    This decorator class was created for use in r3tagger
    (https://github.com/r3/r3tagger) as a means of mitigating the
    musicbrainz api requirement that queries may not exceed one
    per five seconds (or something like that).
"""

from __future__ import print_function
import datetime
import threading
import sched
import time


class Backoff():
    """Delays execution of a decorated function
        Backoff maintains information about the next free time to call the
        decorated function. The delay is set as the first parameter to the
        decorator. This may be set multiple times (once per decorated
        function), but only the last argument will be used. Functions
        needing to wait for invocation will be queued up by the Backoff
        class and later resolved when the delay has lapsed.

        The first decorated method invoked will resolve immediately,
        whereupon the delay will be updated and subsequent invocations
        of decorated methods will be delayed.
    """

    delay = None
    next_call = datetime.datetime.now()
    blocking = True

    def __init__(self, seconds, blocking=None):
        if blocking is not None:
            self._set_blocking(blocking)

        self._set_delay(seconds)

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if self.free():
                func(*args, **kwargs)
                self._update()
            else:
                self._schedule(func, *args, **kwargs)

        return wrapper

    @classmethod
    def _schedule(cls, func, *args, **kwargs):
        """Non-blocking scheduling of function to be resolved after delay"""

        def days_to_seconds(days):
            return days * 24 * 60

        def synch_event(func, *args, **kwargs):
            def event():
                func(*args, **kwargs)

            return event

        backoff = cls.next_call - datetime.datetime.now()
        seconds = days_to_seconds(backoff.days) + backoff.seconds

        if not cls.blocking:
            action = threading.Timer(seconds, func, args, kwargs)
            action.start()
        else:
            priority = 1
            scheduler = sched.scheduler(time.time, time.sleep)
            event = synch_event(func, *args, **kwargs)
            scheduler.enter(seconds, priority, event, ())
            scheduler.run()

        cls._update()

    @classmethod
    def _update(cls):
        """Update the delay to indicate that an action has been taken"""
        cls.next_call += cls.delay

    @classmethod
    def _set_delay(cls, seconds):
        """Set the delay (in seconds) for decorated functions"""
        cls.delay = datetime.timedelta(seconds=1) * seconds

    @classmethod
    def _set_blocking(cls, blocking):
        """Set synch/asynch scheduling"""
        cls.blocking = blocking

    @classmethod
    def free(cls):
        """Indicates that the delay is elapsed"""
        return datetime.datetime.now() >= cls.next_call

if __name__ == '__main__':

    invoked_time = {}
    last_resolution = datetime.datetime.now()

    # Decorated function:
    @Backoff(5)
    def simple_func(name):
        resolved = datetime.datetime.now()
        elapsed = resolved - invoked_time[name]
        print("{} has elapsed since invocation".format(elapsed))

        global last_resolution
        if last_resolution:
            transpired = resolved - last_resolution
            print("{} has elapsed since last resolution".format(transpired),
                    end='\n\n')
            last_resolution = resolved

    invoked_time['A'] = datetime.datetime.now()
    simple_func('A')

    invoked_time['B'] = datetime.datetime.now()
    simple_func('B')

    invoked_time['C'] = datetime.datetime.now()
    simple_func('C')

    invoked_time['D'] = datetime.datetime.now()
    simple_func('D')
