"""
Unit tests for base parser
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx.base as apx_base  # noqa E402
from apx.parser import BaseParser, strip_comment  # noqa E402


class TestBaseParser(unittest.TestCase):

    def test_parse_uint8_integer(self):
        input_string = "0"
        parser = BaseParser()
        parser.reset(input_string)
        result = parser.parse_uint8()
        self.assertEqual(result, 0)
        self.assertEqual(parser.read_position, len(input_string))

        input_string = "255"
        parser.reset(input_string)
        result = parser.parse_uint8()
        self.assertEqual(result, 255)
        self.assertEqual(parser.read_position, len(input_string))

        input_string = "-1"
        parser.reset(input_string)
        result = parser.parse_uint8()
        self.assertEqual(result, None)
        self.assertEqual(parser.read_position, 0)

        input_string = "256"
        parser.reset(input_string)
        result = parser.parse_uint8()
        self.assertEqual(result, None)
        self.assertEqual(parser.read_position, 0)

        input_string = "0x0"
        parser.reset(input_string)
        result = parser.parse_uint8()
        self.assertEqual(result, 0)
        self.assertEqual(parser.read_position, len(input_string))

        input_string = "0x00"
        parser.reset(input_string)
        result = parser.parse_uint8()
        self.assertEqual(result, 0)
        self.assertEqual(parser.read_position, len(input_string))

        input_string = "0xff"
        parser.reset(input_string)
        result = parser.parse_uint8()
        self.assertEqual(result, 255)
        self.assertEqual(parser.read_position, len(input_string))

        input_string = "0x12"
        parser.reset(input_string)
        result = parser.parse_uint8()
        self.assertEqual(result, 0x12)
        self.assertEqual(parser.read_position, len(input_string))

        input_string = "0x100"
        parser.reset(input_string)
        result = parser.parse_uint8()
        self.assertEqual(result, None)
        self.assertEqual(parser.read_position, 0)

    def test_string_literal_empty_string(self):
        input_string = '""'
        parser = BaseParser()
        parser.reset(input_string)
        result, value = parser.parse_string_literal()
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertEqual(value, "")

    def test_string_literal(self):
        input_string = '"Hello World"'
        parser = BaseParser()
        parser.reset(input_string)
        result, value = parser.parse_string_literal()
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertEqual(value, "Hello World")

    def test_string_literal_with_escaped_characters(self):
        input_string = '"Hello \\\"World\\\""'
        parser = BaseParser()
        parser.reset(input_string)
        result, value = parser.parse_string_literal()
        self.assertEqual(result, apx_base.Result.NO_ERROR)
        self.assertEqual(value, "Hello \"World\"")

    def test_remove_line_comment(self):
        input_string = 'R"MyPort"C(0,3):=3#Comment'
        expected_string1 = 'R"MyPort"C(0,3):=3'
        expected_string2 = 'R"MyPort"C(0,3):=3 '
        processed_string = strip_comment(input_string)
        self.assertEqual(processed_string, expected_string1)

        input_string = 'R"MyPort"C(0,3):=3 #Comment'
        processed_string = strip_comment(input_string)
        self.assertEqual(processed_string, expected_string2)

        input_string = 'R"MyPort"C(0,3):=3 # Comment'
        processed_string = strip_comment(input_string)
        self.assertEqual(processed_string, expected_string2)
