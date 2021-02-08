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

from ..scorelib.state import *

class TransactionType:
    UNINITIALIZED = 0
    OUTGOING = 1
    INCOMING = 2
    CLAIM_ISCORE = 3


class Transaction:

    _NAME = "TRANSACTION"

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        name = f"{Transaction._NAME}_{uid}"
        self._type = StateDB(f"{name}_type", db, value_type=TransactionType)
        self._created_timestamp = VarDB(f"{name}_created_timestamp", db, value_type=int)
        self._created_txhash = VarDB(f"{name}_created_txhash", db, value_type=bytes)
        self._uid = uid
        self._name = name

    def build(self, txtype: int, timestamp: int, created_txhash: bytes) -> None:
        self._type.set(txtype)
        self._created_timestamp.set(timestamp)
        self._created_txhash.set(created_txhash)

    # ================================================
    #  Internal methods
    # ================================================
    def serialize(self) -> dict:
        return {
            "uid": self._uid,
            "type": self._type.get_name(),
            "created_txhash": f"0x{bytes.hex(self._created_txhash.get())}" if self._created_txhash.get() else "None",
            "created_timestamp": self._created_timestamp.get(),
        }
