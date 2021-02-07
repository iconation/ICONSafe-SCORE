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
from ..scorelib.id_factory import IdFactory
from ..type_converter.type_converter import *


class SubOutgoingTransactionParam(TypedDict):
    destination: str
    method_name: str
    params: str
    amount: int
    description: str


class TransactionParam(TypedDict):
    name: str
    type: str
    value: str


class SubOutgoingTransactionFactory:

    _NAME = "SUB_OUTGOING_TRANSACTION_FACTORY"

    # ================================================
    #  Checks
    # ================================================
    @staticmethod
    def _check_params_format_convertible(params: List[TransactionParam]):
        for param in params:
            ScoreTypeConverter.convert(param["type"], param["value"])

    @staticmethod
    def create(db: IconScoreDatabase, params: SubOutgoingTransactionParam) -> int:

        destination: Address = Address.from_string(params["destination"])
        method_name: str = params["method_name"]
        tx_params: str = params["params"]
        amount: int = int(params["amount"], 0)
        description: str = params["description"]

        # --- Checks ---
        if tx_params:
            SubOutgoingTransactionFactory._check_params_format_convertible(json_loads(tx_params))

        if not destination.is_contract and (method_name or tx_params):
            raise IconScoreException("Cannot set a method name or params to a EOA transfer transaction")

        # --- OK from here ---
        uid = IdFactory(SubOutgoingTransactionFactory._NAME, db).get_uid()

        sub_tx = SubOutgoingTransaction(uid, db)
        sub_tx._destination.set(destination)
        sub_tx._method_name.set(method_name)
        sub_tx._params.set(tx_params)
        sub_tx._amount.set(amount)
        sub_tx._description.set(description)

        return uid


class SubOutgoingTransaction:

    _NAME = "SUB_OUTGOING_TRANSACTION"

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, uid: int, db: IconScoreDatabase):
        name = f"{SubOutgoingTransaction._NAME}_{uid}"
        self._destination = VarDB(f"{name}_destination", db, value_type=Address)
        self._method_name = VarDB(f"{name}_method_name", db, value_type=str)
        self._params = VarDB(f"{name}_params", db, value_type=str)
        self._amount = VarDB(f"{name}_amount", db, value_type=int)
        self._description = VarDB(f"{name}_description", db, value_type=str)

    # ================================================
    #  Internal methods
    # ================================================
    def convert_params(self) -> dict:
        params = {}
        if self._params.get() != "":
            for param in json_loads(self._params.get()):
                params[param["name"]] = ScoreTypeConverter.convert(param["type"], param["value"])
        return params

    def serialize(self) -> dict:
        return {
            "destination": str(self._destination.get()),
            "method_name": self._method_name.get(),
            "params": self._params.get(),
            "amount": self._amount.get(),
            "description": self._description.get(),
        }
