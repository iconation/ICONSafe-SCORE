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


class ABCBalanceHistoryManager(InterfaceScore):

    @interface
    def name(self) -> str:
        pass

    @interface
    def get_token_balance_history(self, token: Address, offset: int = 0) -> list:
        pass

    @interface
    def get_balance_history(self, balance_history_uid: int) -> dict:
        pass

    @interface
    def get_balance_trackers(self, offset: int = 0) -> list:
        pass

    @interface
    def add_balance_tracker(self, token: Address) -> None:
        pass

    @interface
    def remove_balance_tracker(self, token: Address) -> None:
        pass

    @interface
    def update_all_balances(self, transaction_uid: int):
        pass


class BalanceHistoryManagerProxy(AddressRegistrarProxy):

    NAME = "BALANCE_HISTORY_MANAGER_PROXY"

    # ================================================
    #  Fields
    # ================================================
    @property
    def balance_history_manager(self):
        address = self.registrar.resolve(BalanceHistoryManagerProxy.NAME)
        if not address:
            raise AddressNotInRegistrar(BalanceHistoryManagerProxy.NAME)
        
        return self.create_interface_score(address, ABCBalanceHistoryManager)
