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
from .address_registrar import *


class ABCTransactionManager(InterfaceScore):
    
    @interface
    def name(self) -> str:
        pass

    @interface
    def force_cancel_transaction(self, transaction_uid: int) -> None:
        pass

    @interface
    def claim_iscore(self, claimer: Address) -> None:
        pass

    @interface
    def get_transaction(self, transaction_uid: int) -> dict:
        pass

    @interface
    def get_waiting_transactions(self, offset: int = 0) -> list:
        pass

    @interface
    def get_all_transactions(self, offset: int = 0) -> list:
        pass

    @interface
    def get_executed_transactions(self, offset: int = 0) -> list:
        pass

    @interface
    def get_rejected_transactions(self, offset: int = 0) -> list:
        pass

    @interface
    def get_waiting_transactions_count(self) -> int:
        pass

    @interface
    def get_all_transactions_count(self) -> int:
        pass

    @interface
    def get_executed_transactions_count(self) -> int:
        pass

    @interface
    def get_rejected_transactions_count(self) -> int:
        pass
    
    @interface
    def fallback(self):
        pass

    @interface
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        pass

    @interface
    def handle_incoming_transaction(self, token: Address, source: Address, amount: int) -> None:
        pass

    @interface
    def try_execute_waiting_transactions(self) -> None:
        pass
    
    @interface
    def submit_transaction(self, sub_transactions: str, wallet_owner: Address) -> None:
        pass

    @interface
    def confirm_transaction(self, transaction_uid: int, wallet_owner: Address) -> None:
        pass

    @interface
    def reject_transaction(self, transaction_uid: int, wallet_owner: Address) -> None:
        pass

    @interface
    def revoke_transaction(self, transaction_uid: int, wallet_owner: Address) -> None:
        pass

    @interface
    def cancel_transaction(self, transaction_uid: int, wallet_owner: Address) -> None:
        pass

class TransactionManagerProxy(AddressRegistrarProxy):

    NAME = "TRANSACTION_MANAGER_PROXY"

    # ================================================
    #  Fields
    # ================================================
    @property
    def transaction_manager(self):
        address = self.registrar.resolve(TransactionManagerProxy.NAME)
        if not address:
            raise AddressNotInRegistrar(TransactionManagerProxy.NAME)
        
        return self.create_interface_score(address, ABCTransactionManager)

