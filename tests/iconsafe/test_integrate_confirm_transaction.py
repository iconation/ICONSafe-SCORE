# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
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

import json

from tests.msw_utils import ICONSafeTests
from tests.utils import *


class TestIntegrateConfirmTransaction(ICONSafeTests):

    def setUp(self):
        super().setUp()

    def test_confirm_transaction_validate_wallet_owner(self):
        # submit transaction
        result = self.set_wallet_owners_required(2)
        txuid = self.get_transaction_execution_success_uid(result)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # check confirmation count(should be 1)
        executed_transaction = self.get_executed_transactions_count()
        self.assertEqual(1, executed_transaction)

        # check wallet_owner who has confirmed transaction
        transaction = self.get_transaction(txuid)
        owner_uid = self.get_wallet_owner_uid(self._operator.get_address())
        self.assertEqual(owner_uid, transaction["confirmations"][0])

        # submit transaction 2
        result = self.set_wallet_owners_required(3)
        txuid = self.get_transaction_created_uid(result)
        # result = self.confirm_transaction(txuid, from_=self._operator)

        # failure case: confirm transaction with invalid owner
        result = self.confirm_transaction(txuid, from_=self._attacker, success=False)
        expected_revert_massage = f'{self._attacker.get_address()}'
        actual_revert_massage = result['failure']['message']
        self.assertEqual(expected_revert_massage, actual_revert_massage)

        # success case: confirm transaction with valid owner(_owner2)
        valid_owner = self._owner2
        result = self.confirm_transaction(txuid, from_=valid_owner, success=True)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # check wallet_owners who has confirmed transaction(should be owner1, owner2)
        transaction = self.get_transaction(txuid)
        operator_uid = self.get_wallet_owner_uid(self._operator.get_address())
        owner2_uid = self.get_wallet_owner_uid(self._owner2.get_address())
        self.assertEqual([operator_uid, owner2_uid], transaction["confirmations"])

        # check if transaction executed flag switched to True
        self.assertEqual("EXECUTED", transaction['state'])

        # check if transaction executed successfully (req = 3)
        required = self.get_wallet_owners_required()
        self.assertEqual(3, required)

    def test_confirm_transaction_validate_confirms(self):
        # submit transaction
        result = self.set_wallet_owners_required(2)

        txuid = self.get_transaction_confirmed_uid(result)
        transaction = self.get_transaction(txuid)

        # check confirmation count(should be 1)
        self.assertEqual(len(transaction['confirmations']), 1)

        # failure case: try to confirm using already confirmed owner(owner1)
        confirmed_owner = self._operator
        result = self.confirm_transaction(txuid, from_=self._operator, success=False)
        expected_revert_massage = f"('OUTGOING_TRANSACTION_{txuid}_state_STATEDB', 'EXECUTED', 'WAITING')"
        actual_revert_massage = result['failure']['message']
        self.assertEqual(expected_revert_massage, actual_revert_massage)

        # check confirmation count(should be 1)
        transaction = self.get_transaction(txuid)
        self.assertEqual(len(transaction['confirmations']), 1)

        # check wallet_owner who has confirmed transaction
        transaction = self.get_transaction(txuid)
        owner_uid = self.get_wallet_owner_uid(self._operator.get_address())
        self.assertEqual(owner_uid, transaction["confirmations"][0])

    def test_confirm_transaction_validate_transaction(self):
        result = self.set_wallet_owners_required(2)

        # failure case: confirming transaction on not existing transaction id
        unknown_txid = 123
        result = self.confirm_transaction(unknown_txid, from_=self._operator, success=False)

        expected_revert_massage = f"('TRANSACTION_{unknown_txid}_type_STATEDB', 'UNINITIALIZED', 'OUTGOING')"
        actual_revert_massage = result['failure']['message']
        self.assertEqual(expected_revert_massage, actual_revert_massage)

    def test_confirm_transaction_execute_transaction_failure(self):
        result = self.set_wallet_owners_required(2)

        # failure case: if confirmed transaction is not valid (e.g. invalid balance)
        # should be failed but confirm count should be 2.
        result = self.msw_transfer_icx("hx0000000000000000000000000000000000000000", 10 * 10**100)
        txuid = self.get_transaction_created_uid(result)
        # result = self.confirm_transaction(txuid, from_=self._operator)

        # confirm transaction
        # Fail should occur
        result = self.confirm_transaction(txuid, from_=self._owner2)
        txuid, error = self.get_transaction_execution_failure_uid(result)
        self.assertEqual(error, f"OutOfBalanceException('Out of balance')")

        # check if transaction is not executed
        self.assertEqual("FAILED", self.get_transaction(txuid)['state'])

        # check wallet_owners who has confirmed transaction (should be owner1 and owner2)
        transaction = self.get_transaction(txuid)
        self.assertEqual(len(transaction['confirmations']), 2)
        operator_uid = self.get_wallet_owner_uid(self._operator.get_address())
        owner2_uid = self.get_wallet_owner_uid(self._owner2.get_address())
        self.assertEqual([operator_uid, owner2_uid], transaction["confirmations"])
