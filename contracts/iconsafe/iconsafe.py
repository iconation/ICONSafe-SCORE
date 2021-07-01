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

from ..interfaces.iconsafe import *
from ..interfaces.transaction_manager import *
from ..interfaces.balance_history_manager import *
from ..interfaces.wallet_owners_manager import *
from ..interfaces.event_manager import *
from ..interfaces.wallet_settings_manager import *
from ..interfaces.address_book import *
from ..interfaces.irc2 import *
from ..balance_history_manager.consts import *
from ..domain.domain import *

from .consts import *

class ICONSafe(
    IconScoreBase,
    IconScoreMaintenance,
    IconScoreVersion,

    # Proxies
    BalanceHistoryManagerProxy,
    EventManagerProxy,
    TransactionManagerProxy,
    WalletOwnersManagerProxy,
    WalletSettingsManagerProxy
):
    _NAME = "ICONSafe"

    # ================================================
    #  Event Logs
    # ================================================

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

    def on_install(self, registrar_address: Address) -> None:
        super().on_install()
        self.set_registrar_address(registrar_address)
        self.maintenance_disable()
        self.version_update(VERSION)

    def on_update(self, registrar_address: Address) -> None:
        super().on_update()

        # if self.is_less_than_target_version('1.0.0'):
        #     self._migrate_v1_0_0()

        self.version_update(VERSION)

    @external(readonly=True)
    def name(self) -> str:
        return ICONSafe._NAME

    # ================================================
    #  Token External methods
    # ================================================
    @payable
    @check_maintenance
    def fallback(self):
        transaction_mgr = self.registrar.resolve(TransactionManagerProxy.NAME)
        self.icx.transfer(transaction_mgr, self.msg.value)
        self.transaction_manager.handle_incoming_transaction(ICX_TOKEN_ADDRESS, self.msg.sender, self.msg.value)

    @external
    @check_maintenance
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        transaction_mgr = self.registrar.resolve(TransactionManagerProxy.NAME)
        irc2 = self.create_interface_score(self.msg.sender, IRC2Interface)
        irc2.transfer(transaction_mgr, _value, _data)
        self.transaction_manager.handle_incoming_transaction(self.msg.sender, _from, _value)

    # ================================================
    #  BalanceHistoryManager External methods
    # ================================================
    # --- OnlyMultisigOwner ---
    @external
    @only_multisig_owner
    @check_maintenance
    def add_balance_tracker(self, token: Address) -> None:
        self.balance_history_manager.add_balance_tracker(token)

    @external
    @only_multisig_owner
    @check_maintenance
    def remove_balance_tracker(self, token: Address) -> None:
        self.balance_history_manager.remove_balance_tracker(token)

    # --- ReadOnly ---
    @external(readonly=True)
    def get_token_balance_history(self, token: Address, offset: int = 0) -> list:
        return self.balance_history_manager.get_token_balance_history(token, offset)

    @external(readonly=True)
    def get_balance_history(self, balance_history_uid: int) -> dict:
        return self.balance_history_manager.get_balance_history(balance_history_uid)

    @external(readonly=True)
    def get_balance_trackers(self, offset: int = 0) -> list:
        return self.balance_history_manager.get_balance_trackers(offset)

    # ================================================
    #  AddressRegistrar External methods
    # ================================================
    # --- ReadOnly ---
    @external(readonly=True)
    def resolve(self, name: str) -> Address:
        return self.registrar.resolve(name)

    @external(readonly=True)
    def reverse_resolve(self, address: Address) -> str:
        return self.registrar.reverse_resolve(address)

    @external(readonly=True)
    def resolve_many(self, names: List[str]) -> List[Address]:
        return self.registrar.resolve_many(names)

    @external(readonly=True)
    def reverse_resolve_many(self, addresses: List[Address]) -> List[str]:
        return self.registrar.reverse_resolve_many(addresses)

    @external(readonly=True)
    def get_owners(self, offset: int = 0) -> list:
        return self.registrar.get_owners(offset)

    @external(readonly=True)
    def get_domain(self) -> dict:
        addresses = self.registrar.resolve_many(DOMAIN_NAMES)
        result = {}
        for index, address in enumerate(addresses):
            result[DOMAIN_NAMES[index]] = address
        return result

    # ================================================
    #  EventManager External methods
    # ================================================
    # --- ReadOnly ---
    @external(readonly=True)
    def get_events(self, offset: int = 0) -> list:
        return self.event_manager.get_events(offset)

    # ================================================
    #  AddressBook External methods
    # ================================================
    # --- OnlyTransactionManager ---
    @external
    @only_transaction_manager
    @check_maintenance
    def book_register(self, name: str, address: Address) -> None:
        self.address_book.book_register(name, address)

    @external
    @only_transaction_manager
    @check_maintenance
    def book_unregister(self, name: str) -> None:
        self.address_book.book_unregister(name)

    # --- ReadOnly ---
    @external(readonly=True)
    def book_resolve(self, name: str) -> Address:
        return self.address_book.book_resolve(name)

    @external(readonly=True)
    def book_resolve_many(self, names: List[str]) -> List[Address]:
        return self.address_book.book_resolve_many(names)

    @external(readonly=True)
    def book_reverse_resolve(self, address: Address) -> str:
        return self.address_book.book_reverse_resolve(address)

    @external(readonly=True)
    def book_reverse_resolve_many(self, addresses: List[Address]) -> List[str]:
        return self.address_book.book_reverse_resolve_many(addresses)

    # ================================================
    #  TransactionManager External methods
    # ================================================
    # --- OnlyTransactionManager ---
    @external
    @only_transaction_manager
    @check_maintenance
    def force_cancel_transaction(self, transaction_uid: int) -> None:
        self.transaction_manager.force_cancel_transaction(transaction_uid)

    # --- OnlyMultisigOwner ---
    @external
    @only_multisig_owner
    @check_maintenance
    def submit_transaction(self, sub_transactions: str) -> None:
        wallet_owner = self.msg.sender
        self.transaction_manager.submit_transaction(sub_transactions, wallet_owner)

    @external
    @only_multisig_owner
    @check_maintenance
    def confirm_transaction(self, transaction_uid: int) -> None:
        wallet_owner = self.msg.sender
        self.transaction_manager.confirm_transaction(transaction_uid, wallet_owner)

    @external
    @only_multisig_owner
    @check_maintenance
    def reject_transaction(self, transaction_uid: int) -> None:
        wallet_owner = self.msg.sender
        self.transaction_manager.reject_transaction(transaction_uid, wallet_owner)

    @external
    @only_multisig_owner
    @check_maintenance
    def revoke_transaction(self, transaction_uid: int) -> None:
        wallet_owner = self.msg.sender
        self.transaction_manager.revoke_transaction(transaction_uid, wallet_owner)

    @external
    @only_multisig_owner
    @check_maintenance
    def cancel_transaction(self, transaction_uid: int) -> None:
        wallet_owner = self.msg.sender
        self.transaction_manager.cancel_transaction(transaction_uid, wallet_owner)

    @external
    @only_multisig_owner
    @check_maintenance
    def claim_iscore(self) -> None:
        claimer = self.msg.sender
        self.transaction_manager.claim_iscore(claimer)

    # --- ReadOnly ---
    @external(readonly=True)
    def get_transaction(self, transaction_uid: int) -> dict:
        return self.transaction_manager.get_transaction(transaction_uid)

    @external(readonly=True)
    def get_waiting_transactions(self, offset: int = 0) -> list:
        return self.transaction_manager.get_waiting_transactions(offset)

    @external(readonly=True)
    def get_all_transactions(self, offset: int = 0) -> list:
        return self.transaction_manager.get_all_transactions(offset)

    @external(readonly=True)
    def get_executed_transactions(self, offset: int = 0) -> list:
        return self.transaction_manager.get_executed_transactions(offset)

    @external(readonly=True)
    def get_rejected_transactions(self, offset: int = 0) -> list:
        return self.transaction_manager.get_rejected_transactions(offset)

    @external(readonly=True)
    def get_waiting_transactions_count(self) -> int:
        return self.transaction_manager.get_waiting_transactions_count()

    @external(readonly=True)
    def get_all_transactions_count(self) -> int:
        return self.transaction_manager.get_all_transactions_count()

    @external(readonly=True)
    def get_executed_transactions_count(self) -> int:
        return self.transaction_manager.get_executed_transactions_count()

    @external(readonly=True)
    def get_rejected_transactions_count(self) -> int:
        return self.transaction_manager.get_rejected_transactions_count()

    # ================================================
    #  WalletOwnersManager External methods
    # ================================================
    # --- OnlyWallet ---
    @external
    @only_transaction_manager
    @check_maintenance
    def add_wallet_owner(self, address: Address, name: str) -> None:
        self.wallet_owners_manager.add_wallet_owner(address, name)

    @external
    @only_transaction_manager
    @check_maintenance
    def remove_wallet_owner(self, wallet_owner_uid: int) -> None:
        self.wallet_owners_manager.remove_wallet_owner(wallet_owner_uid)

    @external
    @only_transaction_manager
    @check_maintenance
    def replace_wallet_owner(self, old_wallet_owner_uid: int, new_address: Address, new_name: str) -> None:
        self.wallet_owners_manager.replace_wallet_owner(old_wallet_owner_uid, new_address, new_name)

    @external
    @only_transaction_manager
    @check_maintenance
    def set_wallet_owners_required(self, owners_required: int) -> None:
        self.wallet_owners_manager.set_wallet_owners_required(owners_required)
        self.transaction_manager.try_execute_waiting_transactions()

    # --- ReadOnly ---
    @external(readonly=True)
    def get_wallet_owners(self, offset: int = 0) -> list:
        return self.wallet_owners_manager.get_wallet_owners(offset)

    @external(readonly=True)
    def get_wallet_owner(self, wallet_owner_uid: int) -> dict:
        return self.wallet_owners_manager.get_wallet_owner(wallet_owner_uid)

    @external(readonly=True)
    def get_wallet_owner_uid(self, address: Address) -> int:
        return self.wallet_owners_manager.get_wallet_owner_uid(address)

    @external(readonly=True)
    def get_wallet_owners_count(self) -> int:
        return self.wallet_owners_manager.get_wallet_owners_count()

    @external(readonly=True)
    def is_wallet_owner(self, address: Address) -> bool:
        return self.wallet_owners_manager.is_wallet_owner(address)

    @external(readonly=True)
    def get_wallet_owners_required(self) -> int:
        return self.wallet_owners_manager.get_wallet_owners_required()

    # ================================================
    #  WalletSettingsManager External methods
    # ================================================
    # --- OnlyMultisigOwner ---
    @external
    @only_multisig_owner
    @check_maintenance
    def set_safe_name(self, safe_name: str) -> None:
        self.wallet_settings_manager.set_safe_name(safe_name)

    # --- ReadOnly ---
    @external(readonly=True)
    def get_safe_name(self) -> str:
        return self.wallet_settings_manager.get_safe_name()
