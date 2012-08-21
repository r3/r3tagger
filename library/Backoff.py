#!/usr/bin/env python
"""Backoff Decorator

https://github.com/r3

Author: Ryan Roler (ryan.roler@gmail.com)
Date: 07/17/2012
License: LGPL
Requires: Python 2 or 3

Description:
    Creates a 'Backoff' class to be used as a decorator for functions that
    require a delay between the resolutions of those functions. The delay
    blocks until the function is invoked.

        @Backoff(seconds=5)
        def func_needing_delay():
            pass
"""

from __future__ import print_function
import datetime

from time import sleep


class Backoff(object):
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

    def __init__(self, seconds):
        self._set_delay(seconds)

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if self.free():
                self._update()
                return func(*args, **kwargs)
            else:
                return self._schedule(func, *args, **kwargs)

        return wrapper

    @classmethod
    def _schedule(cls, func, *args, **kwargs):
        """Blocks until the next available call time and invokes function"""
        def days_to_seconds(days):
            return days * 24 * 60

        backoff = cls.next_call - datetime.datetime.now()
        seconds = days_to_seconds(backoff.days) + backoff.seconds

        sleep(seconds)
        cls._update()
        return func(*args, **kwargs)

    @classmethod
    def _update(cls):
        """Update the delay to indicate that an action has been taken"""
        cls.next_call += cls.delay

    @classmethod
    def _set_delay(cls, seconds):
        """Set the delay (in seconds) for decorated functions"""
        cls.delay = datetime.timedelta(seconds=1) * seconds

    @classmethod
    def free(cls):
        """Indicates that the delay is elapsed"""
        return datetime.datetime.now() >= cls.next_call

if __name__ == '__main__':

    invoked_time = {}
    last_resolution = datetime.datetime.now()

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
