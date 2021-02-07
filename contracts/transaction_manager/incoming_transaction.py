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

from .transaction import *

class IncomingTransactionFactory:

    @staticmethod
    def create(db: IconScoreDatabase, transaction_uid: int, txhash: bytes, timestamp: int, token: Address, source: Address, amount: int) -> int:

        transaction = IncomingTransaction(transaction_uid, db)
        transaction.build(TransactionType.INCOMING, timestamp, txhash)
        transaction.set(token, source, amount)

        return transaction_uid


class IncomingTransaction(Transaction):

    _NAME = "INCOMING_TRANSACTION"

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        super().__init__(uid, db)
        name = f"{IncomingTransaction._NAME}_{uid}"
        self._token = VarDB(f"{name}_token", db, value_type=Address)
        self._source = VarDB(f"{name}_source", db, value_type=Address)
        self._amount = VarDB(f"{name}_amount", db, value_type=int)
    
    def set(self, token: Address, source: Address, amount: int) -> None:
        self._token.set(token)
        self._source.set(source)
        self._amount.set(amount)

    # ================================================
    #  Internal methods
    # ================================================
    def serialize(self) -> dict:
        result = super().serialize()

        return {
            **result, 
            "token": str(self._token.get()), 
            "source": str(self._source.get()), 
            "amount": self._amount.get()
        }
