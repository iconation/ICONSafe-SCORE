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
from ..scorelib.set import *
from ..scorelib.state import *

from .sub_outgoing_transaction import *
from .transaction import *


class OutgoingTransactionNotParticipated(Exception):
    pass


class OutgoingTransactionAlreadyParticipated(Exception):
    pass


class OutgoingTransactionHasParticipation(Exception):
    pass


class OutgoingTransactionState:
    UNINITIALIZED = 0
    WAITING = 1
    EXECUTED = 2
    CANCELLED = 3
    FAILED = 4
    REJECTED = 5


class OutgoingTransactionFactory:
    @staticmethod
    def _convert_sub_transactions(params: str) -> List[SubOutgoingTransactionParam]:
        return json_loads(params)

    @staticmethod
    def create(db: IconScoreDatabase, transaction_uid: int, txhash: bytes, timestamp: int, sub_transactions: str) -> int:

        # --- Checks ---
        sub_transactions = OutgoingTransactionFactory._convert_sub_transactions(sub_transactions)

        # --- OK from here ---
        transaction = OutgoingTransaction(transaction_uid, db)
        transaction.build(TransactionType.OUTGOING, timestamp, txhash)

        transaction._state.set(OutgoingTransactionState.WAITING)

        for sub_transaction in sub_transactions:
            sub_transaction_uid = SubOutgoingTransactionFactory.create(db, sub_transaction)
            transaction._sub_transactions.put(sub_transaction_uid)

        return transaction_uid


class OutgoingTransaction(Transaction):

    _NAME = "OUTGOING_TRANSACTION"

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        super().__init__(uid, db)
        name = f"{OutgoingTransaction._NAME}_{uid}"
        self._confirmations = SetDB(f"{name}_confirmations", db, value_type=int, order=True)
        self._rejections = SetDB(f"{name}_rejections", db, value_type=int, order=True)
        self._state = StateDB(f"{name}_state", db, value_type=OutgoingTransactionState)
        self._sub_transactions = ArrayDB(f"{name}_sub_transactions", db, value_type=int)
        self._executed_timestamp = VarDB(f"{name}_executed_timestamp", db, value_type=int)
        self._executed_txhash = VarDB(f"{name}_executed_txhash", db, value_type=bytes)
        self._db = db

    # ================================================
    #  Private methods
    # ================================================
    def _has_participated(self, wallet_owner_uid: int) -> bool:
        return self.has_confirmed(wallet_owner_uid) or self.has_rejected(wallet_owner_uid)

    # ================================================
    #  Checks
    # ================================================
    def check_has_participated(self, wallet_owner_uid: int) -> None:
        if not self._has_participated(wallet_owner_uid):
            raise OutgoingTransactionNotParticipated(self._name, wallet_owner_uid)

    def check_hasnt_participated(self, wallet_owner_uid: int) -> None:
        if self._has_participated(wallet_owner_uid):
            raise OutgoingTransactionAlreadyParticipated(self._name, wallet_owner_uid)

    def check_no_participation(self) -> None:
        if len(self._confirmations) != 0 or len(self._rejections) != 0:
            raise OutgoingTransactionHasParticipation(self._name)

    def has_confirmed(self, wallet_owner_uid: int) -> bool:
        return wallet_owner_uid in self._confirmations

    def has_rejected(self, wallet_owner_uid: int) -> bool:
        return wallet_owner_uid in self._rejections

    # ================================================
    #  Internal methods
    # ================================================
    def serialize(self) -> dict:
        result = super().serialize()
        return {
            **result,
            "confirmations": list(self._confirmations),
            "rejections": list(self._rejections),
            "state": self._state.get_name(),
            "sub_transactions": [SubOutgoingTransaction(sub_transaction_uid, self._db).serialize() for sub_transaction_uid in self._sub_transactions],
            "executed_timestamp": self._executed_timestamp.get(),
            "executed_txhash": f"0x{bytes.hex(self._executed_txhash.get())}" if self._executed_txhash.get() else "None",
        }
