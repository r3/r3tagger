#!/usr/bin/env python
"""Backoff Decorator

https://github.com/r3

Author: Ryan Roler (ryan.roler@gmail.com)
Date: 07/13/2012
License: LGPL
Requires: Python 2 or 3

Description:
    Creates a 'Backoff' class to be used as a decorator for functions that
    require a non-blocking delay between the resolutions of those functions.

        from backoff import Backoff

        @Backoff
        def func_needing_delay():
            pass

        Backoff.set_delay(seconds=5)

    This decorator class was created for use in r3tagger
    (https://github.com/r3/r3tagger) as a means of mitigating the
    musicbrainz api requirement that queries may not exceed one
    per five seconds (or something like that).
"""

from __future__ import print_function
import datetime
import threading


class Backoff():
    """Delays execution of a decorated function
        Backoff maintains information about the next free time to call the
        decorated function. The delay between invocations is set using the
        `set_delay` method which will affect all decorated functions.
        Setting the delay can only be done once in the lifetime of the
        Backoff class. Functions needing to wait for invocation will be
        queued up by the Backoff class and later resolved when the delay
        has lapsed.

        The first decorated method invoked will resolve immediately,
        whereupon the delay will be updated and subsequent invocations
        of decorated methods will be delayed.
    """

    delay = None
    next_call = datetime.datetime.now()

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        if self.free():
            self.func(*args, **kwargs)
            self._update()
        else:
            self._schedule(self.func, *args, **kwargs)

    @classmethod
    def _schedule(cls, func, *args, **kwargs):
        """Non-blocking scheduling of function following elapse of delay"""

        def days_to_seconds(days):
            return days * 24 * 60

        backoff = cls.next_call - datetime.datetime.now()
        seconds = days_to_seconds(backoff.days) + backoff.seconds
        action = threading.Timer(seconds, func, args, kwargs)
        action.start()
        cls._update()

    @classmethod
    def _update(cls):
        """Update the delay to indicate that an action has been taken"""
        cls.next_call += cls.delay

    @classmethod
    def set_delay(cls, seconds):
        """Set the delay (in seconds) for decorated functions"""
        if not cls.delay:
            cls.delay = datetime.timedelta(seconds=1) * seconds
        else:
            raise TypeError("Further modification of delay is not supported")

    @classmethod
    def free(cls):
        """Indicates that the delay is elapsed"""
        return datetime.datetime.now() >= cls.next_call


if __name__ == '__main__':
    delay = 5
    Backoff.set_delay(delay)

    invoked_time = {}
    last_resolution = None

    # Decorated function:
    @Backoff
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
        else:
            last_resolution = resolved
            print("First function to resolve.", end='\n\n')

    invoked_time['A'] = datetime.datetime.now()
    simple_func('A')

    invoked_time['B'] = datetime.datetime.now()
    simple_func('B')

    invoked_time['C'] = datetime.datetime.now()
    simple_func('C')

    invoked_time['D'] = datetime.datetime.now()
    simple_func('D')
