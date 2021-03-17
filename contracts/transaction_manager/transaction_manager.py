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
from ..scorelib.linked_list import *

from ..interfaces.transaction_manager import *
from ..interfaces.balance_history_manager import *
from ..interfaces.wallet_owners_manager import *
from ..interfaces.event_manager import *
from ..balance_history_manager.consts import *
from ..domain.domain import *

from .transaction import *
from .transaction_factory import *
from .consts import *

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

    @external(readonly=True)
    def name(self) -> str:
        return TransactionManager._NAME

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
                # Avoid re-entrancy vulnerability by setting the transaction state before the call
                transaction._state.set(OutgoingTransactionState.EXECUTED)
                
                # Rational behind calling _call_transaction as an external method instead of an internal method:
                # If a multisigned transaction fails during the execution of any subtx (for any reason, such as no balance in the multisig wallet), 
                # we don't want the whole transaction to fail, because we want to return a TransactionExecutionFailure eventlog and set the transaction state to OutgoingTransactionState.FAILED.
                # As _call_transaction calls an external contract that may fail, if it fails we need a mechanism for reverting the state database from the changes of *all* subtx, 
                # to its previous state before the call. Usually we call "revert()" for that, but we can't, as previously stated we need to change the state of the transaction to FAILED.
                # In order to fix that issue, we call _call_transaction method as an external contract :
                # if any subtx raises an error, all the database changes are rollbacked to its state before the external call by SCORE design.
                proxy = self.create_interface_score(self.address, CallTransactionProxyInterface)
                proxy._call_transaction(transaction_uid)

                # Call success
                self.balance_history_manager.update_all_balances(transaction_uid)
                self.TransactionExecutionSuccess(transaction_uid, wallet_owner_uid)
            
            except BaseException as e:
                # Call failure
                transaction._state.set(OutgoingTransactionState.FAILED)
                self.TransactionExecutionFailure(transaction_uid, wallet_owner_uid, repr(e))

    def __serialize_transaction(self, transaction_uid: int) -> dict:
        transaction = Transaction(transaction_uid, self.db)
        transaction_type = transaction._type.get()

        if transaction_type == TransactionType.OUTGOING:
            return OutgoingTransaction(transaction_uid, self.db).serialize()
        elif transaction_type == TransactionType.INCOMING:
            return IncomingTransaction(transaction_uid, self.db).serialize()
        elif transaction_type == TransactionType.CLAIM_ISCORE:
            return ClaimIscoreTransaction(transaction_uid, self.db).serialize()
        else:
            raise InvalidTransactionType(transaction._type.get())
 
    def __handle_incoming_transaction(self, token: Address, source: Address, amount: int) -> int:
        if amount > 0:
            transaction_uid = TransactionFactory.create(self.db, TransactionType.INCOMING, self.tx.hash, self.now(), token, source, amount)
            self.__handle_transaction(transaction_uid)
 
    def __handle_claim_iscore_transaction(self, claimer: Address) -> int:
        system_score = self.create_interface_score(SYSTEM_SCORE_ADDRESS, InterfaceSystemScore)
        iscore = system_score.queryIScore(self.address)['iscore']

        before = self.icx.get_balance(self.address)
        system_score.claimIScore()
        after = self.icx.get_balance(self.address)
        amount = after - before

        if iscore > 0:
            claimer_uid = self.wallet_owners_manager.get_wallet_owner_uid(claimer)
            transaction_uid = TransactionFactory.create(self.db, TransactionType.CLAIM_ISCORE, self.tx.hash, self.now(), amount, iscore, claimer_uid)
            self.__handle_transaction(transaction_uid)

    def __handle_transaction(self, transaction_uid: int) -> None:
        self._all_transactions.append(transaction_uid)
        self.balance_history_manager.update_all_balances(transaction_uid)

    # ================================================
    #  Public External methods
    # ================================================
    @payable
    @only_iconsafe
    def fallback(self):
        # Access
        #   - Only ICONSafe Proxy contract
        # Description 
        #   - Method called on ICX received
        # Parameters 
        #   - Nothing
        # Returns
        #   - Nothing
        # Throws
        #   - AddressNotInRegistrar
        #   - SenderNotIconSafeException

        # All checks are already done : 
        # -> only ICONSafe contract should be able to call this method
        pass

    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        # Access
        #   - Only ICONSafe Proxy contract
        # Description 
        #   - Method called on IRC2 token received
        # Parameters 
        #   - _from : Sender address
        #   - _value : amount of IRC2 token
        #   - _data : optional data
        # Returns
        #   - Nothing
        # Throws
        #   - AddressNotInRegistrar
        #   - SenderNotIconSafeException

        # --- Checks ---
        # -> Check if ICONSafe is the caller of the token transfer
        name = IconSafeProxy.NAME
        iconsafe = self.registrar.resolve(name)
        if not iconsafe:
            raise AddressNotInRegistrar(name)
        if _from != iconsafe:
            raise SenderNotIconSafeException(_from)

    # ================================================
    #  OnlyTransactionManager External methods
    # ================================================
    @external
    @only_transaction_manager
    def _call_transaction(self, transaction_uid: int) -> None:
        # Access
        #   - Only Transaction Manager calling itself
        # Description 
        #   - Try to execute a given transaction
        # Parameters 
        #   - transaction_uid : the transaction UID to execute
        # Returns
        #   - Nothing
        # Throws
        #   - AddressNotInRegistrar
        #   - SenderNotTransactionManagerException

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
                self.call(addr_to=destination, func_name=method_name, kw_dict=params, amount=amount)
            else:
                self.icx.transfer(destination, amount)

    # ================================================
    #  OnlyIconsafe External methods
    # ================================================
    @external
    @only_iconsafe
    def handle_incoming_transaction(self, token: Address, source: Address, amount: int) -> None:
        # Access
        #   - Only ICONSafe Proxy contract
        # Description 
        #   - Handle an incoming token transfer from any address
        # Parameters 
        #   - token : the token address (ICX_TOKEN_ADDRESS for ICX)
        #   - source : the sender address
        #   - amount : amount of token
        # Returns
        #   - Same than BalanceHistoryManager.update_all_balances
        # Throws
        #   - Same than BalanceHistoryManager.update_all_balances

        self.__handle_incoming_transaction(token, source, amount)

    @external
    @only_iconsafe
    def force_cancel_transaction(self, transaction_uid: int) -> None:
        # Access
        #   - Only ICONSafe Proxy contract
        # Description 
        #   - Cancel an outgoing pending transaction, even if it has some confirmations or rejections
        # Parameters 
        #   - transaction_uid : the transaction uid to cancel
        # Returns
        #   - Emits TransactionCancelled
        # Throws
        #   - InvalidState (wrong transaction state, it needs to be pending and outgoing)

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
        # Access
        #   - Only ICONSafe Proxy contract
        # Description 
        #   - Submit a new pending transaction for a vote and confirm it for the submitter 
        # Parameters 
        #   - sub_transactions : JSON formated method parameters
        # Returns
        #   - Emits TransactionCreated
        #   - Same than TransactionManager.confirm_transaction
        # Throws
        #   - Same than TransactionManager.confirm_transaction

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
        # Access
        #   - Only ICONSafe Proxy contract
        # Description 
        #   - Confirm the given transaction for the tx sender. 
        # Parameters 
        #   - transaction_uid : the transaction uid to confirm
        # Returns
        #   - TransactionConfirmed
        #   - TransactionExecutionSuccess or TransactionExecutionFailure
        # Throws
        #   - InvalidState (wrong transaction state, it needs to be pending)
        #   - OutgoingTransactionAlreadyParticipated (the tx sender already participated)
        #   - ItemNotFound (the transaction is not found in the pending transactions list)
        #   - Same than TransactionManager.update_all_balances

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
        # Access
        #   - Only ICONSafe Proxy contract
        # Description 
        #   - Reject (vote no for execution) the given transaction for the tx sender. 
        # Parameters 
        #   - transaction_uid : the transaction uid to cancel
        # Returns
        #   - Emits TransactionRejected
        #   - TransactionRejectionSuccess (if enough reject votes)
        # Throws
        #   - InvalidState (wrong transaction state, it needs to be pending)
        #   - OutgoingTransactionAlreadyParticipated (the tx sender already participated)

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
        # Method
        #   - TransactionManager.revoke_transaction
        # Access
        #   - Only ICONSafe Proxy contract
        # Description 
        #   - Revoke (remove existing vote) the given transaction for the tx sender. 
        # Parameters 
        #   - transaction_uid : the transaction uid to revoke
        # Returns
        #   - Emits TransactionRevoked
        # Throws
        #   - InvalidState (wrong transaction state, it needs to be pending)
        #   - OutgoingTransactionNotParticipated (the tx sender didn’t participated)
        #   - ItemNotFound (the wallet owner who revokes the tx is not found)

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
        # Access
        #   - Only ICONSafe Proxy contract
        # Description 
        #   - Cancel (delete) the given transaction for the tx sender only if there’s no confirmation and no rejection votes
        # Parameters 
        #   - transaction_uid : the transaction uid to cancel
        # Returns
        #   - Emits TransactionCancelled
        # Throws
        #   - InvalidState (wrong transaction state, it needs to be pending)
        #   - OutgoingTransactionHasParticipation (the transaction has participation)
        #   - ItemNotFound (the transaction is not found in the pending or global transactions list)

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
    def claim_iscore(self, claimer: Address) -> None:
        # Access
        #   - Only ICONSafe Proxy contract
        # Description 
        #   - Claim I-Score rewarded from to transaction manager
        # Parameters 
        #   - transaction_uid : the transaction uid to cancel
        # Returns
        #   - Nothing
        # Throws
        #   - Same than TransactionManager.update_all_balances

        self.__handle_claim_iscore_transaction(claimer)

    @external
    @only_iconsafe
    def try_execute_waiting_transactions(self) -> None:
        # Access
        #   - Only ICONSafe Proxy contract
        # Description 
        #   - Try executing pending transactions
        # Parameters 
        #   - Nothing
        # Returns
        #   - TransactionExecutionSuccess or TransactionExecutionFailure
        # Throws
        #   - ItemNotFound (the transaction is not found in the pending transactions list)

        for transaction_uid in list(self._waiting_transactions):
            self.__try_execute_transaction(transaction_uid)

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
