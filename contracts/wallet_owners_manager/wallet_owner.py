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


class WalletOwner:

    _NAME = "WALLET_OWNER"

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        name = f"{WalletOwner._NAME}_{uid}"
        self._address = VarDB(f"{name}_address", db, value_type=Address)
        self._name = VarDB(f"{name}_name", db, value_type=str)
        self._uid = uid
        self._db = db

    # ================================================
    #  Internal methods
    # ================================================
    def same_address(self, target_address: Address) -> bool:
        return self._address.get() == target_address

    def serialize(self) -> dict:
        return {"uid": self._uid, "address": str(self._address.get()), "name": self._name.get()}
