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

from ..scorelib.id_factory import *


class BalanceHistoryFactory:

    _NAME = "BALANCE_HISTORY_FACTORY"

    @staticmethod
    def create(db: IconScoreDatabase, transaction_uid: int, token: Address, balance: int, timestamp: int) -> int:

        balance_history_uid = IdFactory(BalanceHistoryFactory._NAME, db).get_uid()

        balance_history = BalanceHistory(balance_history_uid, db)
        balance_history._token.set(token)
        balance_history._transaction_uid.set(transaction_uid)
        balance_history._balance.set(balance)
        balance_history._timestamp.set(timestamp)

        return balance_history_uid


class BalanceHistory:

    _NAME = "BALANCE_HISTORY"

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        name = f"{BalanceHistory._NAME}_{uid}"
        self._token = VarDB(f"{name}_token", db, value_type=Address)
        self._transaction_uid = VarDB(f"{name}_transaction_uid", db, value_type=int)
        self._balance = VarDB(f"{name}_balance", db, value_type=int)
        self._timestamp = VarDB(f"{name}_timestamp", db, value_type=int)
        self._uid = uid

    # ================================================
    #  Internal methods
    # ================================================
    def serialize(self) -> dict:
        return {
            "uid": self._uid,
            "transaction_uid": self._transaction_uid.get(),
            "token": str(self._token.get()),
            "balance": self._balance.get(),
            "timestamp": self._timestamp.get(),
        }
