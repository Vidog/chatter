#!/usr/bin/env python


from __future__ import absolute_import, division, with_statement
import datetime
import socket
import time
import unittest

from tornado.ioloop import IOLoop
from tornado.netutil import bind_sockets
from tornado.testing import AsyncTestCase, LogTrapTestCase, get_unused_port


class TestIOLoop(AsyncTestCase, LogTrapTestCase):
    def test_add_callback_wakeup(self):
        # Make sure that add_callback from inside a running IOLoop
        # wakes up the IOLoop immediately instead of waiting for a timeout.
        def callback():
            self.called = True
            self.stop()

        def schedule_callback():
            self.called = False
            self.io_loop.add_callback(callback)
            # Store away the time so we can check if we woke up immediately
            self.start_time = time.time()
        self.io_loop.add_timeout(time.time(), schedule_callback)
        self.wait()
        self.assertAlmostEqual(time.time(), self.start_time, places=2)
        self.assertTrue(self.called)

    def test_add_timeout_timedelta(self):
        self.io_loop.add_timeout(datetime.timedelta(microseconds=1), self.stop)
        self.wait()

    def test_multiple_add(self):
        [sock] = bind_sockets(get_unused_port(), '127.0.0.1',
                              family=socket.AF_INET)
        try:
            self.io_loop.add_handler(sock.fileno(), lambda fd, events: None,
                                     IOLoop.READ)
            # Attempting to add the same handler twice fails
            # (with a platform-dependent exception)
            self.assertRaises(Exception, self.io_loop.add_handler,
                              sock.fileno(), lambda fd, events: None,
                              IOLoop.READ)
        finally:
            sock.close()


if __name__ == "__main__":
    unittest.main()
