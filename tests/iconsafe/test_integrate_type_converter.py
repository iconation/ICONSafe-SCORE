# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import iconservice
from iconservice import *
from iconservice.base.exception import InvalidParamsException
import json

from tests.utils import *
from tests.msw_utils import *
from contracts.type_converter.type_converter import ScoreTypeConverter


class TestTypeConverter(ICONSafeTests):
    def setUp(self):
        super().setUp()

    def test_type_converter_param_type(self):
        # failure case: not supported type(dict)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "dict", "")

        # failure case: not supported type(array)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "array", "")

    def test_convert_value_int_from_string(self):
        # success case: convert string type data to int(decimal number)
        expected = 10
        actual = ScoreTypeConverter.convert("int", "10")
        self.assertEqual(expected, actual)

        # success case: convert string type data to int(hex number)
        expected = 16
        actual = ScoreTypeConverter.convert("int", "0x10")
        self.assertEqual(expected, actual)

        # success case: convert string type data to int(hex number)
        expected = -16
        actual = ScoreTypeConverter.convert("int", "-0x10")
        self.assertEqual(expected, actual)

        # failure case: string type data is boolean(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "int", True)

        # failure case: string type data is None(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "int", None)

        # failure case: string type data is string(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "int", "string_data")

    def test_convert_value_int_from_other_type(self):
        # succes case: convert int type data to int
        expected = 10
        actual = ScoreTypeConverter.convert("int", "10")
        self.assertEqual(expected, actual)

        # failure case: value is None(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "int", None)

        # failure case: value is array(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "int", ["array", "test"])

    def test_convert_value_str_from_string(self):
        # success case: convert string type data to string
        expected = "test"
        actual = ScoreTypeConverter.convert("str", "test")
        self.assertEqual(expected, actual)

    def test_convert_value_str_from_other_type(self):
        # failure case: value is boolean(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "str", True)

        # failure case: value is None(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "str", None)

        # failure case: value is int(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "str", 10)

        # failure case: value is array(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "str", ["array", "test"])

    def test_convert_value_bool_from_string(self):
        # success case: convert string type data to True
        expected = True
        actual = ScoreTypeConverter.convert("bool", "1")
        self.assertEqual(expected, actual)

        # success case: convert string type data to False
        expected = False
        actual = ScoreTypeConverter.convert("bool", "0")
        self.assertEqual(expected, actual)

        # failure case: string type data is None(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "bool", None)

        # failure case: string type data is string(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "bool", "string_data")

    def test_convert_value_bool_from_other_type(self):
        # success case: convert value is boolean(true)
        expected = True
        actual = ScoreTypeConverter.convert("bool", "True")
        self.assertEqual(expected, actual)

        # success case: convert value is boolean(false)
        expected = False
        actual = ScoreTypeConverter.convert("bool", "False")
        self.assertEqual(expected, actual)

        # failure case: value is int(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "bool", 10)

        # failure case: value is None(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "bool", None)

        # failure case: value is array(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "bool", ["array", "test"])

    def test_convert_value_address_from_string(self):
        # success case: convert string type address data to address
        addr = create_address()
        expected = addr
        actual = ScoreTypeConverter.convert("Address", str(addr))
        self.assertEqual(expected, actual)

        # failure case: string type data is invalid address format
        self.assertRaises(InvalidParamsException, ScoreTypeConverter.convert, "Address", "hx022f12")

    def test_convert_value_address_from_other_type(self):
        # failure case: value is boolean(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "Address", True)

        # failure case: value is int(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "Address", 10)

        # failure case: value is None(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "Address", None)

        # failure case: value is array(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "Address", ["array", "test"])

    def test_convert_value_bytes_from_bytes(self):
        # success case: convert string type bytes data to bytes
        expected = bytes.fromhex("de ad be ef 00")
        actual = ScoreTypeConverter.convert("bytes", "de ad be ef 00")
        self.assertEqual(expected, actual)

        # failure case: convert string type data to bytes
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "bytes", "test")

    def test_convert_value_bytes_from_other_type(self):
        # failure case: value is boolean(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "bytes", True)

        # failure case: value is None(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "bytes", None)

        # failure case: value is array(type and actual data is not match)
        self.assertRaises(IconScoreException, ScoreTypeConverter.convert, "bytes", ["array", "test"])

    def test_convert_value_list(self):
        array = [
            {"type": "int", "value": "1"},
            {"type": "str", "value": "test"},
        ]
        expected = [1, "test"]

        # failure case: value is boolean(type and actual data is not match)
        actual = ScoreTypeConverter.convert("List", json.dumps(array))
        self.assertEqual(expected, actual)

    def test_convert_value_list_recursive(self):
        array = [
            {"type": "int", "value": "1"},
            {"type": "str", "value": "test"},
            {
                "type": "List",
                "value": """
                [
                    {"type": "int", "value": "1"},
                    {"type": "str", "value": "test"}
                ]
                """,
            },
        ]
        expected = [1, "test", [1, "test"]]
        # failure case: value is boolean(type and actual data is not match)
        actual = ScoreTypeConverter.convert("List", json.dumps(array))
        self.assertEqual(expected, actual)

    def test_convert_value_list(self):
        dict = {
            "Key1": {"type": "int", "value": "1"},
            "Key2": {"type": "str", "value": "test"},
        }
        expected = {"Key1": 1, "Key2": "test"}

        # failure case: value is boolean(type and actual data is not match)
        actual = ScoreTypeConverter.convert("TypedDict", json.dumps(dict))
        self.assertEqual(expected, actual)

    def test_convert_value_list_recursive(self):
        dict = {
            "Key1": {"type": "int", "value": "1"},
            "Key2": {"type": "str", "value": "test"},
            "Key3": {
                "type": "TypedDict",
                "value": """
                {
                    "Key4": {"type": "int", "value": "4"}
                }
                """,
            },
        }
        expected = {"Key1": 1, "Key2": "test", "Key3": {"Key4": 4}}

        # failure case: value is boolean(type and actual data is not match)
        actual = ScoreTypeConverter.convert("TypedDict", json.dumps(dict))
        self.assertEqual(expected, actual)
