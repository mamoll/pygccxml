# Copyright 2014-2016 Insight Software Consortium.
# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0.
# See http://www.boost.org/LICENSE_1_0.txt

import os
import unittest
import platform
import autoconfig
import parser_test_case

from pygccxml import utils
from pygccxml import parser


class tester_impl_t(parser_test_case.parser_test_case_t):

    def __init__(self, architecture, *args):
        parser_test_case.parser_test_case_t.__init__(self, *args)
        self.architecture = architecture
        self.global_ns = None

    def test_enum_patcher(self):
        fix_enum = self.global_ns.free_fun("fix_enum")
        default_val = fix_enum.arguments[0].default_value
        if "CastXML" in utils.xml_generator:
            # Most clean output, no need to patch
            self.assertTrue(default_val == "ns1::ns2::apple")
        else:
            self.assertTrue(default_val == "::ns1::ns2::apple")

        # double_call = declarations.find_declaration(
        # decls, type=declarations.free_function_t, name='double_call' )

    def test_numeric_patcher(self):
        fix_numeric = self.global_ns.free_fun("fix_numeric")
        if 32 == self.architecture:
            if "0.9" in utils.xml_generator:
                if platform.machine() == "x86_64":
                    self.assertTrue(
                        fix_numeric.arguments[0].default_value == "-1u",
                        fix_numeric.arguments[0].default_value)
                else:
                    val = "0xffffffffffffffffu"
                    self.assertTrue(
                        fix_numeric.arguments[0].default_value == val,
                        fix_numeric.arguments[0].default_value)
            else:
                val = "0xffffffffffffffff"
                self.assertTrue(
                    fix_numeric.arguments[0].default_value == val,
                    fix_numeric.arguments[0].default_value)
        else:
            if "CastXML" in utils.xml_generator:
                # Most clean output, no need to patch
                self.assertTrue(
                    fix_numeric.arguments[0].default_value == "(ull)-1",
                    fix_numeric.arguments[0].default_value)
            else:
                self.assertTrue(
                    fix_numeric.arguments[0].default_value == "0ffffffff",
                    fix_numeric.arguments[0].default_value)

    def test_unnamed_enum_patcher(self):
        fix_unnamed = self.global_ns.free_fun("fix_unnamed")
        self.assertTrue(
            fix_unnamed.arguments[0].default_value == "int(::fx::unnamed)")

    def test_function_call_patcher(self):
        fix_function_call = self.global_ns.free_fun("fix_function_call")
        default_val = fix_function_call.arguments[0].default_value
        if "CastXML" in utils.xml_generator:
            # Most clean output, no need to patch
            val = "calc(1, 2, 3)"
            self.assertTrue(default_val == val)
        elif "0.9" in utils.xml_generator:
            val = "function_call::calc(1, 2, 3)"
            self.assertTrue(default_val == val)
        else:
            val = "function_call::calc( 1, 2, 3 )"
            self.assertTrue(default_val == val)

    def test_fundamental_patcher(self):
        fcall = self.global_ns.free_fun("fix_fundamental")
        val = "(unsigned int)(::fundamental::eggs)"
        self.assertTrue(
            fcall.arguments[0].default_value == val)

    def test_constructor_patcher(self):
        typedef__func = self.global_ns.free_fun("typedef__func")
        default_val = typedef__func.arguments[0].default_value
        if "0.9" in utils.xml_generator:
            val = "typedef_::original_name()"
            self.assertTrue(default_val == val)
        elif "CastXML" in utils.xml_generator:
            # Most clean output, no need to patch
            val = "typedef_::alias()"
            self.assertTrue(default_val == val)
        else:
            val = "::typedef_::alias( )"
            self.assertTrue(default_val == val)
        if 32 == self.architecture:
            clone_tree = self.global_ns.free_fun("clone_tree")
            default_values = []
            if "0.9" in utils.xml_generator:
                default_values = []
            else:
                default_values = [
                    ("vector<std::basic_string<char, std::char_traits<char>," +
                        " std::allocator<char> >,std::allocator" +
                        "<std::basic_string<char, std::char_traits<char>, " +
                        "std::allocator<char> > > >()"),
                    ("vector<std::basic_string<char, std::char_traits<char>," +
                        "std::allocator<char> >,std::allocator" +
                        "<std::basic_string<char, std::char_traits<char>, " +
                        "std::allocator<char> > > >((&allocator" +
                        "<std::basic_string<char, std::char_traits<char>, " +
                        "std::allocator<char> > >()))")]
                self.assertTrue(
                    clone_tree.arguments[0].default_value in default_values)


class tester_32_t(tester_impl_t):
    global_ns = None

    def __init__(self, *args):
        tester_impl_t.__init__(self, 32, *args)

    def setUp(self):
        if not tester_32_t.global_ns:
            reader = parser.source_reader_t(self.config)
            tester_32_t.global_ns = reader.read_file(
                "patcher.hpp")[0].top_parent
        self.global_ns = tester_32_t.global_ns


class tester_64_t(tester_impl_t):
    global_ns = None

    def __init__(self, *args):
        tester_impl_t.__init__(self, 64, *args)
        self.original_get_architecture = utils.get_architecture

    def setUp(self):
        self.original_get_architecture = utils.get_architecture
        utils.get_architecture = lambda: 64

        if not tester_64_t.global_ns:
            reader = parser.source_reader_t(self.config)
            if "castxml" not in self.config.xml_generator:
                tester_64_t.global_ns = reader.read_xml_file(
                    os.path.join(
                        autoconfig.data_directory,
                        "patcher_tester_64bit.xml"))[0].top_parent
            else:
                tester_64_t.global_ns = reader.read_file(
                    "patcher.hpp")[0].top_parent
        self.global_ns = tester_64_t.global_ns

    def tearDown(self):
        utils.get_architecture = self.original_get_architecture


def create_suite():
    suite = unittest.TestSuite()
    if "castxml" not in autoconfig.cxx_parsers_cfg.gccxml.xml_generator:
        suite.addTest(unittest.makeSuite(tester_32_t))
    suite.addTest(unittest.makeSuite(tester_64_t))
    return suite


def run_suite():
    unittest.TextTestRunner(verbosity=2).run(create_suite())

if __name__ == "__main__":
    run_suite()
