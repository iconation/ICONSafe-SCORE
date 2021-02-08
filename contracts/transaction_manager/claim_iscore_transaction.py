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

from .incoming_transaction import *
from ..balance_history_manager.consts import *

class ClaimIscoreTransactionFactory:

    @staticmethod
    def create(db: IconScoreDatabase, transaction_uid: int, txhash: bytes, timestamp: int, amount: int, iscore: int, claimer_uid: int) -> int:

        token = ICX_TOKEN_ADDRESS
        source = SYSTEM_SCORE_ADDRESS
        transaction = ClaimIscoreTransaction(transaction_uid, db)
        transaction.build(TransactionType.CLAIM_ISCORE, timestamp, txhash)
        transaction.set(token, source, amount, iscore, claimer_uid)

        return transaction_uid


class ClaimIscoreTransaction(IncomingTransaction):

    _NAME = "CLAIM_ISCORE_TRANSACTION"

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        super().__init__(uid, db)
        name = f"{ClaimIscoreTransaction._NAME}_{uid}"
        self._iscore = VarDB(f"{name}_iscore", db, value_type=int)
        self._claimer_uid = VarDB(f"{name}_claimer_uid", db, value_type=int)
    
    def set(self, token: Address, source: Address, amount: int, iscore: int, claimer_uid: int) -> None:
        super().set(token, source, amount)
        self._iscore.set(iscore)
        self._claimer_uid.set(claimer_uid)

    # ================================================
    #  Internal methods
    # ================================================
    def serialize(self) -> dict:
        result = super().serialize()

        return {
            **result, 
            "iscore": self._iscore.get(),
            "claimer_uid": self._claimer_uid.get()
        }
