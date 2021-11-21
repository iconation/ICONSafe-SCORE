# -*- coding: utf-8 -*-

# Copyright 2021 ICONation
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

from iconservice import *


class ScoreTypeConverter:
    @staticmethod
    def convert(param_type: str, value: str):

        if not isinstance(value, str):
            raise IconScoreException(f"Value type must be str ({value} is {type(value)}).")

        valid_types = {
            "int": ScoreTypeConverter._convert_value_int,
            "str": ScoreTypeConverter._convert_value_string,
            "bool": ScoreTypeConverter._convert_value_bool,
            "Address": ScoreTypeConverter._convert_value_address,
            "bytes": ScoreTypeConverter._convert_value_bytes,
            "List": ScoreTypeConverter._convert_value_list,
            "TypedDict": ScoreTypeConverter._convert_value_typed_dict,
        }

        if not param_type in valid_types.keys():
            raise IconScoreException(f"{param_type} is not supported type (only {valid_types.keys()} are supported)")

        try:
            return valid_types[param_type](value)
        except Exception as e:
            raise IconScoreException(f"Cannot convert {value} from type {param_type}")

    @staticmethod
    def _convert_value_int(value: str) -> int:
        return int(value, 0)

    @staticmethod
    def _convert_value_string(value: str) -> str:
        return value

    @staticmethod
    def _convert_value_bool(value: str) -> bool:
        if value == "True" or value == "0x1" or value == "1":
            return True
        if value == "False" or value == "0x0" or value == "0":
            return False
        raise IconScoreException("Invalid bool value")

    @staticmethod
    def _convert_value_address(value: str) -> Address:
        return Address.from_string(value)

    @staticmethod
    def _convert_value_bytes(value: str) -> bytes:
        if value.startswith("0x"):
            return bytes.fromhex(value[2:])
        else:
            return bytes.fromhex(value)

    @staticmethod
    def _convert_value_list(value: str) -> list:
        items = json_loads(value)
        if type(items) != list:
            raise IconScoreException(f"Invalid variable type, excepted list, found {type(items)}")

        result = []
        for item in items:
            result.append(ScoreTypeConverter.convert(item["type"], item["value"]))

        return result

    @staticmethod
    def _convert_value_typed_dict(value: str) -> dict:
        items = json_loads(value)
        if type(items) != dict:
            raise IconScoreException(f"Invalid variable type, excepted dict, found {type(items)}")

        result = {}
        for key, item in items.items():
            result[key] = ScoreTypeConverter.convert(item["type"], item["value"])

        return result
