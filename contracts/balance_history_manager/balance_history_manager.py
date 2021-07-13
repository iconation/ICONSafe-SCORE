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

from ..scorelib.maintenance import *
from ..scorelib.version import *
from ..scorelib.set import *
from ..scorelib.linked_list import *

from ..interfaces.balance_history_manager import *
from ..interfaces.transaction_manager import *
from ..interfaces.event_manager import *
from ..interfaces.irc2 import *
from ..domain.domain import *

from .balance_history import *
from .consts import *


class BalanceHistoryManager(
    IconScoreBase,
    IconScoreMaintenance,
    IconScoreVersion,

    EventManagerProxy
):
    _NAME = "BALANCE_HISTORY_MANAGER"

    # ================================================
    #  Event Logs
    # ================================================
    @add_event
    @eventlog(indexed=1)
    def BalanceHistoryCreated(self, balance_history_uid: int):
        pass

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        # List of tokens that are actively tracked for the balance history
        self._tracked_balance_history = SetDB(f"{BalanceHistoryManager._NAME}_tokens_tracked", self.db, value_type=Address)

    def on_install(self, registrar_address: Address) -> None:
        super().on_install()
        self.set_registrar_address(registrar_address)
        self.maintenance_disable()
        self.version_update(VERSION)

        # Track ICX balance by default
        self._tracked_balance_history.add(ICX_TOKEN_ADDRESS)

    def on_update(self, registrar_address: Address) -> None:
        super().on_update()

        # if self.is_less_than_target_version('1.0.0'):
        #     self._migrate_v1_0_0()

        self.version_update(VERSION)

    @external(readonly=True)
    def name(self) -> str:
        return BalanceHistoryManager._NAME

    # ================================================
    #  Private methods
    # ================================================
    def __token_balance_history(self, token: Address) -> UIDLinkedListDB:
        # List of balance history items for any token
        return UIDLinkedListDB(f"{BalanceHistoryManager._NAME}_{str(token)}_balance_history", self.db)

    def __update_token_balance(self, transaction_uid: int, token: Address, current_balance: int) -> None:
        # Check for update in the last balance history item
        token_balance_history = self.__token_balance_history(token)

        if len(token_balance_history) > 0:
            last_balance_history_uid = token_balance_history.head_value()
            last_balance_history = BalanceHistory(last_balance_history_uid, self.db)
            if last_balance_history._balance.get() == current_balance:
                # The last balance is the same, no need to update the balance history
                return

        balance_history_uid = BalanceHistoryFactory.create(self.db, transaction_uid, token, current_balance, self.now())
        token_balance_history.prepend(balance_history_uid)
        self.BalanceHistoryCreated(balance_history_uid)
    
    def __get_total_staked_icx(self) -> int:
        amount = 0
        transaction_mgr = self.registrar.resolve(TransactionManagerProxy.NAME)
        
        try:
            system_score = self.create_interface_score(SYSTEM_SCORE_ADDRESS, InterfaceSystemScore)
            staked = system_score.getStake(transaction_mgr)

            # Currently staked
            if "stake" in staked:
                amount += staked["stake"]
            # Unstaking
            if "unstakes" in staked:
                for unstake in staked["unstakes"]:
                    amount += unstake["unstake"]
        except:
            # t-bears may not have installed system_score_address yet
            pass
        
        return amount

    def __update_icx_balance(self, transaction_uid: int) -> None:
        # ICX Balance = Liquid ICX + Staked ICX
        transaction_mgr = self.registrar.resolve(TransactionManagerProxy.NAME)
        if transaction_mgr:
            current_balance = self.icx.get_balance(transaction_mgr)
            current_balance += self.__get_total_staked_icx()
        else:
            current_balance = 0

        self.__update_token_balance(transaction_uid, ICX_TOKEN_ADDRESS, current_balance)

    def __update_irc2_balance(self, transaction_uid: int, token: Address) -> None:
        irc2 = self.create_interface_score(token, IRC2Interface)
        transaction_mgr = self.registrar.resolve(TransactionManagerProxy.NAME)
        if transaction_mgr:
            current_balance = irc2.balanceOf(transaction_mgr)
        else:
            current_balance = 0

        self.__update_token_balance(transaction_uid, token, current_balance)

    def __update_all_balances(self, transaction_uid: int):
        for token in self._tracked_balance_history:
            if token == ICX_TOKEN_ADDRESS:
                self.__update_icx_balance(transaction_uid)
            else:
                self.__update_irc2_balance(transaction_uid, token)

    # ================================================
    #  OnlyTransactionManager External methods
    # ================================================
    @external
    @only_transaction_manager
    def update_all_balances(self, transaction_uid: int):
        # Access
        #   - Only Transaction Manager Contract
        # Description 
        #   - Update the balances of all tracked balances
        # Parameters 
        #   - transaction_uid : the transaction UID
        # Returns
        #   - Emit BalanceHistoryCreated
        # Throws
        #   - Nothing
        self.__update_all_balances(transaction_uid)

    # ================================================
    #  OnlyICONSafe External methods
    # ================================================
    @external
    @only_iconsafe
    def add_balance_tracker(self, token: Address) -> None:
        # Access
        #   - Only ICONSafe Proxy Contract
        # Description 
        #   - Add a new balance to the tracked tokens
        # Parameters 
        #   - token: the token governance contract address
        # Returns
        #   - Same than update_all_balances
        # Throws
        #   - Nothing
        self._tracked_balance_history.add(token)
        self.__update_all_balances(SYSTEM_TRANSACTION_UID)

    @external
    @only_iconsafe
    def remove_balance_tracker(self, token: Address) -> None:
        # Access
        #   - Only ICONSafe Proxy Contract
        # Description 
        #   - Remove an existing balance from the tracked tokens
        # Parameters 
        #   - token: the token governance contract address
        # Returns
        #   - Same than update_all_balances
        # Throws
        #   - ItemNotFound
        self._tracked_balance_history.remove(token)
        self.__update_all_balances(SYSTEM_TRANSACTION_UID)

    # ================================================
    #  ReadOnly External methods
    # ================================================
    @external(readonly=True)
    def get_token_balance_history(self, token: Address, offset: int = 0) -> list:
        return [
            self.get_balance_history(balance_history_uid) 
            for balance_history_uid in self.__token_balance_history(token).select(offset)
        ]

    @external(readonly=True)
    def get_balance_history(self, balance_history_uid: int) -> dict:
        return BalanceHistory(balance_history_uid, self.db).serialize()

    @external(readonly=True)
    def get_balance_trackers(self, offset: int = 0) -> list:
        return self._tracked_balance_history.select(offset)
