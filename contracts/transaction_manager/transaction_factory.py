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

from .outgoing_transaction import *
from .incoming_transaction import *
from .claim_iscore_transaction import *


class InvalidTransactionType(Exception):
    pass


class TransactionFactory:

    _NAME = "TRANSACTION_FACTORY"

    @staticmethod
    def create(db: IconScoreDatabase, transaction_type: int, txhash: bytes, timestamp: int, *args) -> int:

        transaction_uid = IdFactory(TransactionFactory._NAME, db).get_uid()

        if transaction_type == TransactionType.OUTGOING:
            return OutgoingTransactionFactory.create(db, transaction_uid, txhash, timestamp, *args)
        elif transaction_type == TransactionType.INCOMING:
            return IncomingTransactionFactory.create(db, transaction_uid, txhash, timestamp, *args)
        elif transaction_type == TransactionType.CLAIM_ISCORE:
            return ClaimIscoreTransactionFactory.create(db, transaction_uid, txhash, timestamp, *args)
        else:
            raise InvalidTransactionType(TransactionFactory._NAME, transaction_type)
