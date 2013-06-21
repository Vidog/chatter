#!/usr/bin/env python

from __future__ import absolute_import, division, with_statement
import sys
import unittest

TEST_MODULES = [
    'tornado.httputil.doctests',
    'tornado.iostream.doctests',
    'tornado.util.doctests',
    'tornado.test.auth_test',
    'tornado.test.curl_httpclient_test',
    'tornado.test.escape_test',
    'tornado.test.gen_test',
    'tornado.test.httpclient_test',
    'tornado.test.httpserver_test',
    'tornado.test.httputil_test',
    'tornado.test.import_test',
    'tornado.test.ioloop_test',
    'tornado.test.iostream_test',
    'tornado.test.locale_test',
    'tornado.test.options_test',
    'tornado.test.process_test',
    'tornado.test.simple_httpclient_test',
    'tornado.test.stack_context_test',
    'tornado.test.template_test',
    'tornado.test.testing_test',
    'tornado.test.twisted_test',
    'tornado.test.util_test',
    'tornado.test.web_test',
    'tornado.test.wsgi_test',
]


def all():
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)

if __name__ == '__main__':
    # The -W command-line option does not work in a virtualenv with
    # python 3 (as of virtualenv 1.7), so configure warnings
    # programmatically instead.
    import warnings
    # Be strict about most warnings.  This also turns on warnings that are
    # ignored by default, including DeprecationWarnings and
    # python 3.2's ResourceWarnings.
    warnings.filterwarnings("error")
    # setuptools sometimes gives ImportWarnings about things that are on
    # sys.path even if they're not being used.
    warnings.filterwarnings("ignore", category=ImportWarning)
    # Tornado generally shouldn't use anything deprecated, but some of
    # our dependencies do (last match wins).
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("error", category=DeprecationWarning,
                            module=r"tornado\..*")

    import tornado.testing
    kwargs = {}
    if sys.version_info >= (3, 2):
        # HACK:  unittest.main will make its own changes to the warning
        # configuration, which may conflict with the settings above
        # or command-line flags like -bb.  Passing warnings=False
        # suppresses this behavior, although this looks like an implementation
        # detail.  http://bugs.python.org/issue15626
        kwargs['warnings'] = False
    tornado.testing.main(**kwargs)
