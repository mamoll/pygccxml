# Copyright 2014-2016 Insight Software Consortium.
# Distributed under the Boost Software License, Version 1.0.
# See http://www.boost.org/LICENSE_1_0.txt

import unittest
import parser_test_case

from pygccxml import parser
from pygccxml import declarations


class tester_t(parser_test_case.parser_test_case_t):

    def __init__(self, *args):
        parser_test_case.parser_test_case_t.__init__(self, *args)
        self.header = 'non_copyable_classes.hpp'
        self.global_ns = None

    def setUp(self):
        if not self.global_ns:
            decls = parser.parse([self.header], self.config)
            self.global_ns = declarations.get_global_namespace(decls)
            self.global_ns.init_optimizer()

    def test(self):

        """
        Search for two classes which can not be copied.

        See bug #13

        Covers two cases for the moment
        1) non copyable class
        2) non copyable const (fundamental type)
        3) non copyable const (class type)
        4) non copyable const (array type)

        """

        MainFoo1 = self.global_ns.class_('MainFoo1')
        self.assertTrue(declarations.is_noncopyable(MainFoo1))

        MainFoo2 = self.global_ns.class_('MainFoo2')
        self.assertTrue(declarations.is_noncopyable(MainFoo2))

        MainFoo3 = self.global_ns.class_('MainFoo3')
        self.assertTrue(declarations.is_noncopyable(MainFoo3))

        MainFoo4 = self.global_ns.class_('MainFoo4')
        self.assertTrue(declarations.is_noncopyable(MainFoo4))


def create_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(tester_t))
    return suite


def run_suite():
    unittest.TextTestRunner(verbosity=2).run(create_suite())

if __name__ == "__main__":
    run_suite()
