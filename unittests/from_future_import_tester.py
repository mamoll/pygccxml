# Copyright 2014-2016 Insight Software Consortium.
# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0.
# See http://www.boost.org/LICENSE_1_0.txt

from __future__ import unicode_literals

import unittest
import parser_test_case
from pygccxml import declarations
from pygccxml import parser


class tester_t(parser_test_case.parser_test_case_t):

    """
    Some methods like namespace() verify if their argument is a string.
    Check if this works well and if it is compatible with the
    from __future__ import unicode_literals statement.

    """

    def __init__(self, *args):
        parser_test_case.parser_test_case_t.__init__(self, *args)
        self.fname = "basic.hpp"

    def test_namespace_argument_string(self):
        # Check with a string
        self.global_ns.namespace("test")

    def test_namespace_argument_int(self):
        # Check with an int, should raise an error
        self.assertRaises(AssertionError, lambda: self.global_ns.namespace(1))

    def setUp(self):
        reader = parser.source_reader_t(self.config)
        decls = reader.read_file(self.fname)
        self.global_ns = declarations.get_global_namespace(decls)


def create_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(tester_t))
    return suite


def run_suite():
    unittest.TextTestRunner(verbosity=2).run(create_suite())

if __name__ == "__main__":
    run_suite()
