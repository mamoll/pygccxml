# Copyright 2014-2016 Insight Software Consortium.
# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0.
# See http://www.boost.org/LICENSE_1_0.txt

import pprint
import sys
import unittest
import autoconfig


class parser_test_case_t(unittest.TestCase):

    CXX_PARSER_CFG = None

    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        if self.CXX_PARSER_CFG:
            self.config = self.CXX_PARSER_CFG.clone()
        elif autoconfig.cxx_parsers_cfg.gccxml:
            self.config = autoconfig.cxx_parsers_cfg.gccxml.clone()
        else:
            pass

    def _test_type_composition(self, type_, expected_compound, expected_base):
        self.assertTrue(
            isinstance(type_, expected_compound),
            "the compound type('%s') should be '%s'" %
            (type_.decl_string, expected_compound.__name__))
        self.assertTrue(
            isinstance(type_.base, expected_base),
            "base type('%s') should be '%s'" %
            (type_.decl_string, expected_base.__name__))

    def _test_calldef_return_type(self, calldef, expected_type):
        self.assertTrue(
            isinstance(calldef.return_type, expected_type),
            ("the function's '%s' expected return type is '%s' and in " +
                "reality it is different('%s')") %
            (calldef.name, expected_type.__name__,
             calldef.return_type.__class__.__name__))

    def _test_calldef_args(self, calldef, expected_args):
        self.assertTrue(
            len(calldef.arguments) == len(expected_args),
            ("the function's '%s' expected number of arguments is '%d' and " +
                "in reality it is different('%d')") %
            (calldef.name, len(expected_args), len(calldef.arguments)))

        for i, expected_arg in enumerate(expected_args):
            arg = calldef.arguments[i]
            self.assertTrue(
                arg == expected_arg,
                ("the function's '%s' expected %d's argument is '%s' and in " +
                    "reality it is different('%s')") %
                (calldef.name, i, pprint.pformat(expected_arg.__dict__),
                 pprint.pformat(arg.__dict__)))

    def _test_calldef_exceptions(self, calldef, exceptions):
        # exceptions is list of classes names
        exception_decls = []
        for name in exceptions:
            exception_decl = self.global_ns.class_(name)
            self.assertTrue(
                exception_decl,
                "unable to find exception class '%s'" %
                name)
            exception_decls.append(exception_decl)
        exception_decls.sort()
        self.assertTrue(
            len(calldef.exceptions) == len(exception_decls),
            ("the function's '%s' expected number of exceptions is '%d' and " +
                "in reality it is different('%d')") %
            (calldef.name,
             len(exception_decls),
             len(calldef.exceptions)))
        exceptions_indeed = sorted(calldef.exceptions[:])
        self.assertTrue(
            exception_decls == exceptions_indeed,
            ("the function's '%s' expected exceptions are '%s' and in " +
                "reality it is different('%s')") %
            (calldef.name,
             pprint.pformat([delc.name for delc in exception_decls]),
             pprint.pformat([delc.name for delc in exceptions_indeed])))

if sys.version_info < (2, 7, 0):
    # Python2.6 does not have the following methods in the unittest module
    parser_test_case_t.assertIn = \
        lambda parser, a1, a2, *args: parser.assertTrue(a1 in a2, args)
    parser_test_case_t.assertNotIn = \
        lambda parser, a1, a2, *args: parser.assertFalse(a1 in a2, args)
