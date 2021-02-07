from iconsdk.builder.transaction_builder import DeployTransactionBuilder
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction
from tests.utils import *

import json
import os
import asyncio

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

def deploy_routine(self, path, params, key, return_dict, lock):
    return_dict[key] = self._deploy_score(path, params=params)['scoreAddress']

class ICONSafeTests(IconIntegrateTestBase):

    ADDRESS_REGISTRAR_PATH = os.path.abspath(os.path.join(DIR_PATH, '../build/address_registrar'))
    ICONSAFE_PATH = os.path.abspath(os.path.join(DIR_PATH, '../build/iconsafe'))
    BALANCE_HISTORY_MANAGER_PATH = os.path.abspath(os.path.join(DIR_PATH, '../build/balance_history_manager'))
    EVENT_MANAGER_PATH = os.path.abspath(os.path.join(DIR_PATH, '../build/event_manager'))
    TRANSACTION_MANAGER_PATH = os.path.abspath(os.path.join(DIR_PATH, '../build/transaction_manager'))
    WALLET_OWNERS_MANAGER_PATH = os.path.abspath(os.path.join(DIR_PATH, '../build/wallet_owners_manager'))
    WALLET_SETTINGS_MANAGER_PATH = os.path.abspath(os.path.join(DIR_PATH, '../build/wallet_settings_manager'))
    IRC2_PROJECT = os.path.abspath(os.path.join(DIR_PATH, './irc2'))

    def setUp(self):
        super().setUp()

        self.icon_service = None

        # install SCORE
        self._operator = self._test1
        self._owner2 = self._wallet_array[0]
        self._owner3 = self._wallet_array[1]
        self._user = self._wallet_array[2]
        self._attacker = self._wallet_array[9]

        self._registrar_address = self._deploy_score(self.ADDRESS_REGISTRAR_PATH, params={})['scoreAddress']
        self._balance_history_manager = self._deploy_score(self.BALANCE_HISTORY_MANAGER_PATH, params={"registrar_address": self._registrar_address})['scoreAddress']
        self._score_address = self._deploy_score(self.ICONSAFE_PATH, params={"registrar_address": self._registrar_address})['scoreAddress']
        self._event_manager = self._deploy_score(self.EVENT_MANAGER_PATH, params={"registrar_address": self._registrar_address})['scoreAddress']
        self._transaction_manager = self._deploy_score(self.TRANSACTION_MANAGER_PATH, params={"registrar_address": self._registrar_address})['scoreAddress']
        self._wallet_settings_manager = self._deploy_score(self.WALLET_SETTINGS_MANAGER_PATH, params={"registrar_address": self._registrar_address})['scoreAddress']
        self._wallet_owners_manager = self._deploy_score(self.WALLET_OWNERS_MANAGER_PATH, params={"registrar_address": self._registrar_address,
                "owners": [{
                    "address": self._operator.get_address(),
                    "name": "operator"
                },
                    {
                    "address": self._owner2.get_address(),
                    "name": "owner2"
                },
                    {
                    "address": self._owner3.get_address(),
                    "name": "owner3"
                }],
                "owners_required": "0x1"
            })['scoreAddress']

        self.register("ADDRESS_REGISTRAR_PROXY", self._registrar_address)
        self.register("ICONSAFE_PROXY", self._score_address)
        self.register("BALANCE_HISTORY_MANAGER_PROXY", self._balance_history_manager)
        self.register("EVENT_MANAGER_PROXY", self._event_manager)
        self.register("TRANSACTION_MANAGER_PROXY", self._transaction_manager)
        self.register("WALLET_SETTINGS_MANAGER_PROXY", self._wallet_settings_manager)
        self.register("WALLET_OWNERS_MANAGER_PROXY", self._wallet_owners_manager)

        for wallet in self._wallet_array:
            icx_transfer_call(super(), self._test1, wallet.get_address(), 100 * 10**18, self.icon_service)

        self._operator_icx_balance = get_icx_balance(super(), address=self._operator.get_address(), icon_service=self.icon_service)
        self._owner2_icx_balance = get_icx_balance(super(), address=self._owner2.get_address(), icon_service=self.icon_service)
        self._irc2_address = self._deploy_irc2(self.IRC2_PROJECT)['scoreAddress']

        irc2_transfer(super(), from_=self._operator, token=self._irc2_address, to_=self._owner2.get_address(), value=0x1000000, icon_service=self.icon_service)
        self._operator_irc2_balance = get_irc2_balance(super(), address=self._operator.get_address(), token=self._irc2_address, icon_service=self.icon_service)
        self._owner2_irc2_balance = get_irc2_balance(super(), address=self._owner2.get_address(), token=self._irc2_address, icon_service=self.icon_service)

    def _deploy_score(self, project, to: str = SCORE_INSTALL_ADDRESS, params={}) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(project)) \
            .params(params) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction in local
        result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in result)

        if result['status'] != 1:
            print(result)

        self.assertEqual(1, result['status'])
        self.assertTrue('scoreAddress' in result)

        return result

    def _deploy_irc2(self, project, to: str = SCORE_INSTALL_ADDRESS) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .params({
                "_initialSupply": 0x100000000000,
                "_decimals": 18,
                "_name": 'StandardToken',
                "_symbol": 'ST',
            }) \
            .from_(self._operator.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(project)) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._operator)

        # process the transaction in local
        result = self.process_transaction(
            signed_transaction, self.icon_service)

        self.assertTrue('status' in result)
        self.assertEqual(1, result['status'])
        self.assertTrue('scoreAddress' in result)

        return result

    def get_executed_transactions_count(self) -> int:
        return int(
            icx_call(
                super(),
                from_=self._operator.get_address(),
                to_=self._score_address,
                method="get_executed_transactions_count",
                icon_service=self.icon_service
            ), 0
        )

    def register(self, name, address, from_=None, success=True):
        return self._do_call(
            from_,
            'register',
            {'name': name,
            'address': address},
            success,
            to_=self._registrar_address
        )

    def unregister(self, name, from_=None, success=True):
        return self._do_call(
            from_,
            'unregister',
            {'name': name},
            success,
            to_=self._registrar_address
        )

    def get_wallet_owners_required(self) -> int:
        return int(
            icx_call(
                super(),
                from_=self._operator.get_address(),
                to_=self._score_address,
                method="get_wallet_owners_required",
                icon_service=self.icon_service
            ), 0
        )

    def is_wallet_owner(self, address: Address) -> bool:
        return int(
            icx_call(
                super(),
                from_=self._operator.get_address(),
                to_=self._score_address,
                method="is_wallet_owner",
                params={"address": address},
                icon_service=self.icon_service
            ), 0
        ) != 0

    def get_waiting_transactions_count(self) -> int:
        return int(
            icx_call(
                super(),
                from_=self._operator.get_address(),
                to_=self._score_address,
                method="get_waiting_transactions_count",
                icon_service=self.icon_service
            ), 0
        )

    def get_waiting_transactions(self, offset: int = 0) -> list:
        return icx_call(
            super(),
            from_=self._operator.get_address(),
            to_=self._score_address,
            method="get_waiting_transactions",
            params={"offset": offset},
            icon_service=self.icon_service
        )

    def get_executed_transactions(self, offset: int = 0) -> list:
        return icx_call(
            super(),
            from_=self._operator.get_address(),
            to_=self._score_address,
            method="get_executed_transactions",
            params={"offset": offset},
            icon_service=self.icon_service
        )

    def get_wallet_owners(self, offset: int = 0) -> list:
        return icx_call(
            super(),
            from_=self._operator.get_address(),
            to_=self._score_address,
            method="get_wallet_owners",
            params={"offset": offset},
            icon_service=self.icon_service
        )

    def get_token_balance_history(self, token: Address, offset: int = 0) -> list:
        return icx_call(
            super(),
            from_=self._operator.get_address(),
            to_=self._score_address,
            method="get_token_balance_history",
            params={"token": str(token), "offset": offset},
            icon_service=self.icon_service
        )

    def get_transaction(self, transaction_uid: int) -> dict:
        """
        {
            "uid": self._uid,
            "destination": str(self._destination.get()),
            "method_name": self._method_name.get(),
            "params": self._params.get(),
            "amount": self._amount.get(),
            "description": self._description.get(),
            "confirmations": list(self._confirmations),
            "state": self._state.get_name()
        }
        """
        return icx_call(
            super(),
            from_=self._operator.get_address(),
            to_=self._score_address,
            method="get_transaction",
            params={"transaction_uid": transaction_uid},
            icon_service=self.icon_service
        )

    def get_wallet_owner_uid(self, address: Address) -> int:
        return int(icx_call(
            super(),
            from_=self._operator.get_address(),
            to_=self._score_address,
            method="get_wallet_owner_uid",
            params={"address": address},
            icon_service=self.icon_service
        ), 0)

    def get_wallet_owners_count(self) -> int:
        return int(icx_call(
            super(),
            from_=self._operator.get_address(),
            to_=self._score_address,
            method="get_wallet_owners_count",
            icon_service=self.icon_service
        ), 0)

    def _do_call(self, from_, method, params, success, to_=None):
        call = transaction_call_success if success else transaction_call_error
        from_ = from_ if from_ else self._operator
        to_ = to_ if to_ else self._score_address
        result = call(super(), from_=from_,
                      to_=to_,
                      method=method,
                      params=params,
                      icon_service=self.icon_service)
        self.assertEqual(int(success), result['status'])
        return result

    def confirm_transaction(self, transaction_uid: int, from_=None, success=True):
        return self._do_call(
            from_,
            'confirm_transaction',
            {'transaction_uid': str(transaction_uid)},
            success
        )

    def reject_transaction(self, transaction_uid: int, from_=None, success=True):
        return self._do_call(
            from_,
            'reject_transaction',
            {'transaction_uid': str(transaction_uid)},
            success
        )

    def revoke_transaction(self, transaction_uid: int, from_=None, success=True):
        return self._do_call(
            from_,
            'revoke_transaction',
            {'transaction_uid': str(transaction_uid)},
            success
        )

    def cancel_transaction(self, transaction_uid: int, from_=None, success=True):
        return self._do_call(
            from_,
            'cancel_transaction',
            {'transaction_uid': str(transaction_uid)},
            success
        )

    def add_balance_tracker(self, token: Address, params=None, from_=None, success=True):
        return self._do_call(
            from_,
            "add_balance_tracker",
            {'token': str(token)},
            success
        )

    def get_transaction_created_uid(self, tx) -> int:
        for eventlog in tx['eventLogs']:
            if eventlog['indexed'][0] == 'TransactionCreated(int,int)':
                return int(eventlog['indexed'][1], 0)

    def get_transaction_cancelled_uid(self, tx) -> int:
        for eventlog in tx['eventLogs']:
            if eventlog['indexed'][0] == 'TransactionCancelled(int,int)':
                return int(eventlog['indexed'][1], 0)

    def get_transaction_confirmed_uid(self, tx) -> int:
        for eventlog in tx['eventLogs']:
            if eventlog['indexed'][0] == 'TransactionConfirmed(int,int)':
                return int(eventlog['indexed'][1], 0)

    def get_transaction_rejected_uid(self, tx) -> int:
        for eventlog in tx['eventLogs']:
            if eventlog['indexed'][0] == 'TransactionRejected(int,int)':
                return int(eventlog['indexed'][1], 0)

    def get_transaction_rejection_success_uid(self, tx) -> int:
        for eventlog in tx['eventLogs']:
            if eventlog['indexed'][0] == 'TransactionRejectionSuccess(int,int)':
                return int(eventlog['indexed'][1], 0)

    def get_transaction_execution_success_uid(self, tx) -> int:
        for eventlog in tx['eventLogs']:
            if eventlog['indexed'][0] == 'TransactionExecutionSuccess(int,int)':
                return int(eventlog['indexed'][1], 0)

    def get_transaction_revoked_uid(self, tx) -> int:
        for eventlog in tx['eventLogs']:
            if eventlog['indexed'][0] == 'TransactionRevoked(int,int)':
                return int(eventlog['indexed'][1], 0)

    def get_transaction_execution_failure_uid(self, tx) -> int:
        for eventlog in tx['eventLogs']:
            if eventlog['indexed'][0] == 'TransactionExecutionFailure(int,int,str)':
                return int(eventlog['indexed'][1], 0), eventlog['data'][1]

    def submit_transaction(self, from_, params, success=True):
        return self._do_call(from_, 'submit_transaction', {'sub_transactions': json.dumps(params)}, success)

    def _create_submit_transaction_params(self, params):
        return {
            "destination": "",
            "method_name": "",
            "params": "",
            "amount": "0",
            "description": "",
            **params
        }

    def set_wallet_owners_required(self, value: int = 3, params=None, from_=None, success=True):
        if not params:
            params = [
                {'name': 'owners_required',
                 'type': 'int',
                 'value': str(value)}
            ]

        if not isinstance(params, str):
            params = json.dumps(params)

        params = self._create_submit_transaction_params(
            {'destination': str(self._score_address),
             'method_name': "set_wallet_owners_required",
             'params': params,
             'description': 'change requirements to 2'})

        return self.submit_transaction(from_, [params], success)

    def force_cancel_transaction(self, transaction_uid: int, from_=None, success=True):
        params = [
            {'name': 'transaction_uid', 'type': 'int', 'value': str(transaction_uid)}
        ]

        params = self._create_submit_transaction_params(
            {'destination': str(self._score_address),
             'method_name': "force_cancel_transaction",
             'params': json.dumps(params),
             'description': f'Force cancel a transaction: {transaction_uid}'})

        return self.submit_transaction(from_, [params], success)

    def add_wallet_owner(self, address: Address, name: str, from_=None, success=True):
        params = [
            {'name': 'address', 'type': 'Address', 'value': address},
            {'name': 'name', 'type': 'str', 'value': name}
        ]

        params = self._create_submit_transaction_params(
            {'destination': str(self._score_address),
             'method_name': "add_wallet_owner",
             'params': json.dumps(params),
             'description': f'Add new owner : {address}'})

        return self.submit_transaction(from_, [params], success)

    def remove_wallet_owner(self, wallet_owner_uid: int, from_=None, success=True):
        params = [
            {'name': 'wallet_owner_uid', 'type': 'int', 'value': str(wallet_owner_uid)},
        ]

        params = self._create_submit_transaction_params(
            {'destination': str(self._score_address),
             'method_name': "remove_wallet_owner",
             'params': json.dumps(params),
             'description': f'Remove owner : {wallet_owner_uid}'})

        return self.submit_transaction(from_, [params], success)

    def replace_wallet_owner(self, old_wallet_owner_uid: int, new_address: Address, new_name: str, from_=None, success=True):
        params = [
            {'name': 'old_wallet_owner_uid', 'type': 'int', 'value': str(old_wallet_owner_uid)},
            {'name': 'new_address', 'type': 'Address', 'value': str(new_address)},
            {'name': 'new_name', 'type': 'str', 'value': str(new_name)}
        ]

        params = self._create_submit_transaction_params(
            {'destination': str(self._score_address),
             'method_name': "replace_wallet_owner",
             'params': json.dumps(params),
             'description': f'Replace owner : {old_wallet_owner_uid} to {new_address} ({new_name})'})

        return self.submit_transaction(from_, [params], success)

    def msw_transfer_irc2(self, token: Address, destination: Address, amount: int, from_=None, success=True):
        params = self.msw_transfer_irc2_params(token, destination, amount)
        return self.submit_transaction(from_, [params], success)

    def msw_transfer_irc2_params(self, token: Address, destination: Address, amount: int):
        params = [
            {'name': '_to', 'type': 'Address', 'value': str(destination)},
            {'name': '_value', 'type': 'int', 'value': str(amount)}
        ]

        return self._create_submit_transaction_params(
            {'destination': str(token),
             'method_name': "transfer",
             'params': json.dumps(params),
             'description': f'Send {amount} IRC2 {(token)} to {destination}'})

    def msw_transfer_icx(self, destination: Address, amount: int, from_=None, success=True):
        params = self.msw_transfer_icx_params(destination, amount)
        return self.submit_transaction(from_, [params], success)

    def msw_transfer_icx_params(self, destination: Address, amount: int):
        return self._create_submit_transaction_params({'destination': str(destination),
                                                       'description': f'Transfer {amount} ICX to {destination}',
                                                       'amount': f'{hex(amount)}'})

    def msw_revert_check(self, token: Address, destination: Address, amount: int, from_=None, success=True):
        params = [
            {'name': '_to', 'type': 'Address', 'value': str(destination)},
            {'name': '_value', 'type': 'int', 'value': str(amount)}
        ]

        params = self._create_submit_transaction_params(
            {'destination': str(token),
             'method_name': "revert_check",
             'params': json.dumps(params),
             'description': f'Revert check'})

        return self.submit_transaction(from_, [params], success)

    def deposit_icx_to_multisig_score(self, value: int):
        return icx_transfer_call(super(), self._operator, self._score_address, value, self.icon_service)

    def send_token(self, value, to):
        return irc2_transfer(
            super(),
            from_=self._operator,
            token=str(self._irc2_address),
            to_=to,
            value=value,
            icon_service=self.icon_service)

    def balance_token(self, address: Address):
        return get_irc2_balance(super(), str(address), str(self._irc2_address), icon_service=self.icon_service)

    def confirm_transaction_created(self, tx):
        txuid = self.get_transaction_created_uid(tx)
        return self.confirm_transaction(txuid)
