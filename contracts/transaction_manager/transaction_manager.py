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
from ..scorelib.exception import *
from ..scorelib.maintenance import *
from ..scorelib.auth import *
from ..scorelib.version import *
from .consts import *

from ..scorelib.linked_list import *
from ..interfaces.transaction_manager import *
from ..interfaces.balance_history_manager import *
from ..interfaces.wallet_owners_manager import *
from ..interfaces.event_manager import *
from ..domain.domain import *
from ..balance_history_manager.consts import *

from .transaction import *
from .transaction_factory import *

class CallTransactionProxyInterface(InterfaceScore):
    @interface
    def _call_transaction(self) -> None:
        pass


class TransactionManager(
    IconScoreBase,
    ABCTransactionManager,
    IconScoreMaintenance,
    IconScoreVersion,
    IconScoreExceptionHandler,

    BalanceHistoryManagerProxy,
    WalletOwnersManagerProxy,
    EventManagerProxy
):

    _NAME = "TRANSACTION_MANAGER"

    # ================================================
    #  Event Logs
    # ================================================
    @add_event
    @eventlog(indexed=1)
    def TransactionCreated(self, transaction_uid: int, wallet_owner_uid: int):
        pass

    @add_event
    @eventlog(indexed=2)
    def TransactionConfirmed(self, transaction_uid: int, wallet_owner_uid: int):
        pass

    @add_event
    @eventlog(indexed=2)
    def TransactionRevoked(self, transaction_uid: int, wallet_owner_uid: int):
        pass

    @add_event
    @eventlog(indexed=2)
    def TransactionRejected(self, transaction_uid: int, wallet_owner_uid: int):
        pass

    @add_event
    @eventlog(indexed=1)
    def TransactionCancelled(self, transaction_uid: int, wallet_owner_uid: int):
        pass

    @add_event
    @eventlog(indexed=1)
    def TransactionExecutionSuccess(self, transaction_uid: int, wallet_owner_uid: int):
        pass

    @add_event
    @eventlog(indexed=1)
    def TransactionRejectionSuccess(self, transaction_uid: int, wallet_owner_uid: int):
        pass

    @add_event
    @eventlog(indexed=1)
    def TransactionExecutionFailure(self, transaction_uid: int, wallet_owner_uid: int, error: str):
        pass

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._waiting_transactions = UIDLinkedListDB(f"{TransactionManager._NAME}_waiting_transactions", self.db)
        self._executed_transactions = UIDLinkedListDB(f"{TransactionManager._NAME}_executed_transactions", self.db)
        self._rejected_transactions = UIDLinkedListDB(f"{TransactionManager._NAME}_rejected_transactions", self.db)
        self._all_transactions = UIDLinkedListDB(f"{TransactionManager._NAME}_all_transactions", self.db)

    @catch_exception
    def on_install(self, registrar_address: Address) -> None:
        super().on_install()
        self.set_registrar_address(registrar_address)
        self.maintenance_disable()
        self.version_update(VERSION)

    @catch_exception
    def on_update(self, registrar_address: Address) -> None:
        super().on_update()

        # if self.is_less_than_target_version('1.0.0'):
        #     self._migrate_v1_0_0()

        self.version_update(VERSION)

    # ================================================
    #  Private methods
    # ================================================
    def __try_execute_transaction(self, transaction_uid: int) -> None:
        transaction = OutgoingTransaction(transaction_uid, self.db)
        wallet_owners_required = self.wallet_owners_manager.get_wallet_owners_required()

        if len(transaction._confirmations) >= wallet_owners_required:
            # Enough confirmations for the current transaction, execute it
            # Move the transaction from the waiting transactions
            self._waiting_transactions.remove(transaction_uid)
            self._executed_transactions.append(transaction_uid)
            transaction._executed_txhash.set(self.tx.hash)

            # Consider the executor as the last added confirmation
            wallet_owner_uid = transaction._confirmations.last()

            try:
                proxy = self.create_interface_score(self.address, CallTransactionProxyInterface)
                proxy._call_transaction(transaction_uid)
                # Call success
                self.balance_history_manager.update_all_balances(transaction_uid)
                transaction._state.set(OutgoingTransactionState.EXECUTED)
                self.TransactionExecutionSuccess(transaction_uid, wallet_owner_uid)
            except BaseException as e:
                transaction._state.set(OutgoingTransactionState.FAILED)
                self.TransactionExecutionFailure(transaction_uid, wallet_owner_uid, repr(e))

    def __serialize_transaction(self, transaction_uid: int) -> dict:
        transaction = Transaction(transaction_uid, self.db)
        transaction_type = transaction._type.get()

        if transaction_type == TransactionType.OUTGOING:
            return OutgoingTransaction(transaction_uid, self.db).serialize()
        elif transaction_type == TransactionType.INCOMING:
            return IncomingTransaction(transaction_uid, self.db).serialize()
        else:
            raise InvalidTransactionType(transaction._type.get())

    def __handle_incoming_transaction(self, token: Address, source: Address, amount: int) -> None:
        # --- OK from here ---
        transaction_uid = TransactionFactory.create(self.db, TransactionType.INCOMING, self.tx.hash, self.now(), token, source, amount)
        self._all_transactions.append(transaction_uid)
        self.balance_history_manager.update_all_balances(transaction_uid)

    # ================================================
    #  Public External methods
    # ================================================
    @payable
    def fallback(self):
        self.__handle_incoming_transaction(ICX_TOKEN_ADDRESS, self.tx.origin, self.msg.value)

    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        self.__handle_incoming_transaction(self.msg.sender, self.tx.origin, _value)

    # ================================================
    #  OnlyDomain External methods
    # ================================================
    @external
    @only_domain
    def try_execute_transaction(self, transaction_uid: int) -> None:
        self.__try_execute_transaction(transaction_uid)

    @external(readonly=True)
    @only_domain
    def get_all_waiting_transactions(self) -> list:
        return [
            self.__serialize_transaction(transaction_uid) 
            for transaction_uid in self._waiting_transactions
        ]

    # ================================================
    #  OnlyTransactionManager External methods
    # ================================================
    @external
    @only_transaction_manager
    def _call_transaction(self, transaction_uid: int) -> None:
        transaction = OutgoingTransaction(transaction_uid, self.db)
        # Get the execution time, even if the subtx fails
        transaction._executed_timestamp.set(self.now())

        # Handle all sub transactions
        for sub_transaction_uid in transaction._sub_transactions:
            sub_transaction = SubOutgoingTransaction(sub_transaction_uid, self.db)

            method_name = sub_transaction._method_name.get() or None
            params = sub_transaction.convert_params()
            destination = sub_transaction._destination.get()
            amount = sub_transaction._amount.get()

            if destination.is_contract and method_name != None:
                self.call(addr_to=destination, func_name=method_name,kw_dict=params, amount=amount)
            else:
                self.icx.transfer(destination, amount)

    # ================================================
    #  OnlyIconsafe External methods
    # ================================================
    @external
    @only_iconsafe
    def force_cancel_transaction(self, transaction_uid: int) -> None:
        transaction = OutgoingTransaction(transaction_uid, self.db)
        wallet_owner_uid = self.wallet_owners_manager.get_wallet_owner_uid(self.tx.origin)

        # --- Checks ---
        transaction._type.check(TransactionType.OUTGOING)
        transaction._state.check(OutgoingTransactionState.WAITING)

        # --- OK from here ---
        transaction._state.set(OutgoingTransactionState.CANCELLED)
        # Remove it from active transactions
        self._waiting_transactions.remove(transaction_uid)
        self._all_transactions.remove(transaction_uid)
        self.TransactionCancelled(transaction_uid, wallet_owner_uid)

    @external
    @only_iconsafe
    def submit_transaction(self, sub_transactions: str) -> None:
        wallet_owner_uid = self.wallet_owners_manager.get_wallet_owner_uid(self.tx.origin)
        
        # --- OK from here ---
        transaction_uid = TransactionFactory.create(self.db, TransactionType.OUTGOING, self.tx.hash, self.now(), sub_transactions)

        self._waiting_transactions.append(transaction_uid)
        self._all_transactions.append(transaction_uid)
        self.TransactionCreated(transaction_uid, wallet_owner_uid)

        # Auto confirm it from the creator
        self.confirm_transaction(transaction_uid)

    @external
    @only_iconsafe
    def confirm_transaction(self, transaction_uid: int) -> None:
        transaction = OutgoingTransaction(transaction_uid, self.db)
        wallet_owner_uid = self.wallet_owners_manager.get_wallet_owner_uid(self.tx.origin)

        # --- Checks ---
        transaction._type.check(TransactionType.OUTGOING)
        transaction._state.check(OutgoingTransactionState.WAITING)
        transaction.check_hasnt_participated(wallet_owner_uid)

        # --- OK from here ---
        transaction._confirmations.add(wallet_owner_uid)
        self.TransactionConfirmed(transaction_uid, wallet_owner_uid)

        self.__try_execute_transaction(transaction_uid)

    @external
    @only_iconsafe
    def reject_transaction(self, transaction_uid: int) -> None:
        transaction = OutgoingTransaction(transaction_uid, self.db)
        wallet_owner_uid = self.wallet_owners_manager.get_wallet_owner_uid(self.tx.origin)

        # --- Checks ---
        transaction._type.check(TransactionType.OUTGOING)
        transaction._state.check(OutgoingTransactionState.WAITING)
        transaction.check_hasnt_participated(wallet_owner_uid)

        # --- OK from here ---
        transaction._rejections.add(wallet_owner_uid)
        self.TransactionRejected(transaction_uid, wallet_owner_uid)
        wallet_owners_required = self.wallet_owners_manager.get_wallet_owners_required()

        if len(transaction._rejections) >= wallet_owners_required:
            # Enough confirmations for the current transaction, reject it

            # Move the transaction from the waiting transactions
            self._waiting_transactions.remove(transaction_uid)
            self._rejected_transactions.append(transaction_uid)

            # Update the transaction state
            transaction._state.set(OutgoingTransactionState.REJECTED)
            self.TransactionRejectionSuccess(transaction_uid, wallet_owner_uid)

    @external
    @only_iconsafe
    def revoke_transaction(self, transaction_uid: int) -> None:
        transaction = OutgoingTransaction(transaction_uid, self.db)
        wallet_owner_uid = self.wallet_owners_manager.get_wallet_owner_uid(self.tx.origin)

        # --- Checks ---
        transaction._type.check(TransactionType.OUTGOING)
        transaction._state.check(OutgoingTransactionState.WAITING)
        transaction.check_has_participated(wallet_owner_uid)

        # --- OK from here ---
        if transaction.has_confirmed(wallet_owner_uid):
            transaction._confirmations.remove(wallet_owner_uid)
        elif transaction.has_rejected(wallet_owner_uid):
            transaction._rejections.remove(wallet_owner_uid)

        self.TransactionRevoked(transaction_uid, wallet_owner_uid)

    @external
    @only_iconsafe
    def cancel_transaction(self, transaction_uid: int) -> None:
        transaction = OutgoingTransaction(transaction_uid, self.db)
        wallet_owner_uid = self.wallet_owners_manager.get_wallet_owner_uid(self.tx.origin)

        # --- Checks ---
        transaction._type.check(TransactionType.OUTGOING)
        transaction._state.check(OutgoingTransactionState.WAITING)
        transaction.check_no_participation()

        # --- OK from here ---
        transaction._state.set(OutgoingTransactionState.CANCELLED)
        # Remove it from active transactions
        self._waiting_transactions.remove(transaction_uid)
        self._all_transactions.remove(transaction_uid)
        self.TransactionCancelled(transaction_uid, wallet_owner_uid)

    @external
    @only_iconsafe
    def claim_iscore(self) -> None:
        system_score = self.create_interface_score(SYSTEM_SCORE_ADDRESS, InterfaceSystemScore)
        system_score.claimIScore()
        # Update balances
        self.balance_history_manager.update_all_balances(SYSTEM_TRANSACTION_UID)

    # ================================================
    #  ReadOnly OnlyICONSafe External methods
    # ================================================
    @external(readonly=True)
    @only_iconsafe
    def get_transaction(self, transaction_uid: int) -> dict:
        return self.__serialize_transaction(transaction_uid)

    @external(readonly=True)
    @only_iconsafe
    def get_waiting_transactions(self, offset: int = 0) -> list:
        return [
            self.__serialize_transaction(transaction_uid) 
            for transaction_uid in self._waiting_transactions.select(offset)
        ]

    @external(readonly=True)
    @only_iconsafe
    def get_all_transactions(self, offset: int = 0) -> list:
        return [
            self.__serialize_transaction(transaction_uid) 
            for transaction_uid in self._all_transactions.select(offset)
        ]

    @external(readonly=True)
    @only_iconsafe
    def get_executed_transactions(self, offset: int = 0) -> list:
        return [
            self.__serialize_transaction(transaction_uid) 
            for transaction_uid in self._executed_transactions.select(offset)
        ]

    @external(readonly=True)
    @only_iconsafe
    def get_rejected_transactions(self, offset: int = 0) -> list:
        return [
            self.__serialize_transaction(transaction_uid) 
            for transaction_uid in self._rejected_transactions.select(offset)
        ]

    @external(readonly=True)
    @only_iconsafe
    def get_waiting_transactions_count(self) -> int:
        return len(self._waiting_transactions)

    @external(readonly=True)
    @only_iconsafe
    def get_all_transactions_count(self) -> int:
        return len(self._all_transactions)

    @external(readonly=True)
    @only_iconsafe
    def get_executed_transactions_count(self) -> int:
        return len(self._executed_transactions)

    @external(readonly=True)
    @only_iconsafe
    def get_rejected_transactions_count(self) -> int:
        return len(self._rejected_transactions)
