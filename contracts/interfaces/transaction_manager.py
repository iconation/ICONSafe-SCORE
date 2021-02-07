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
from ..utility.proxy_score import *


class ABCTransactionManager(ABC):
    
    @abstractmethod
    def force_cancel_transaction(self, transaction_uid: int) -> None:
        pass

    @abstractmethod
    def submit_transaction(self, sub_transactions: str) -> None:
        pass

    @abstractmethod
    def confirm_transaction(self, transaction_uid: int) -> None:
        pass

    @abstractmethod
    def reject_transaction(self, transaction_uid: int) -> None:
        pass

    @abstractmethod
    def revoke_transaction(self, transaction_uid: int) -> None:
        pass

    @abstractmethod
    def cancel_transaction(self, transaction_uid: int) -> None:
        pass

    @abstractmethod
    def claim_iscore(self) -> None:
        pass

    @abstractmethod
    def try_execute_waiting_transactions(self) -> None:
        pass

    @abstractmethod
    def get_transaction(self, transaction_uid: int) -> dict:
        pass

    @abstractmethod
    def get_waiting_transactions(self, offset: int = 0) -> list:
        pass

    @abstractmethod
    def get_all_transactions(self, offset: int = 0) -> list:
        pass

    @abstractmethod
    def get_executed_transactions(self, offset: int = 0) -> list:
        pass

    @abstractmethod
    def get_rejected_transactions(self, offset: int = 0) -> list:
        pass

    @abstractmethod
    def get_waiting_transactions_count(self) -> int:
        pass

    @abstractmethod
    def get_all_transactions_count(self) -> int:
        pass

    @abstractmethod
    def get_executed_transactions_count(self) -> int:
        pass

    @abstractmethod
    def get_rejected_transactions_count(self) -> int:
        pass


class ABCTransactionManagerSystemLevel(ABCTransactionManager):
    
    @abstractmethod
    def fallback(self):
        pass

    @abstractmethod
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        pass

    @abstractmethod
    def get_all_waiting_transactions(self) -> list:
        pass

class TransactionManagerProxy(AddressRegistrarProxy):

    NAME = "TRANSACTION_MANAGER_PROXY"
    TransactionManagerInterface = ProxyScore(ABCTransactionManagerSystemLevel)

    # ================================================
    #  Fields
    # ================================================
    @property
    def transaction_manager(self):
        address = self.registrar.resolve(TransactionManagerProxy.NAME)
        if not address:
            raise AddressNotInRegistrar(TransactionManagerProxy.NAME)
        
        return self.create_interface_score(address, TransactionManagerProxy.TransactionManagerInterface)

