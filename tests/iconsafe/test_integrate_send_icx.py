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

from tests.msw_utils import ICONSafeTests
from tests.utils import *

ICX_FACTOR = 10 ** 18


class TestIntegrateSendIcx(ICONSafeTests):

    def setUp(self):
        super().setUp()

    def test_send_icx_negative_value(self):
        # failure case: submit transaction which send -10 icx to token score
        result = self.msw_transfer_icx(self._irc2_address, -10 * ICX_FACTOR)
        txuid, error = self.get_transaction_execution_failure_uid(result)
        self.assertEqual(error, f"InvalidParamsException('Amount is less than zero')")

        # check if transaction is not executed
        self.assertEqual("FAILED", self.get_transaction(txuid)['state'])

    def test_send_icx_to_score(self):
        result = self.set_wallet_owners_required(2)

        # success case: send icx to SCORE(token score)
        # deposit 100 icx to wallet SCORE
        self.deposit_icx_to_multisig_score(100 * ICX_FACTOR)

        # submit transaction which send 10 icx to token score
        result = self.msw_transfer_icx(self._irc2_address, 10 * ICX_FACTOR)
        txuid = self.get_transaction_created_uid(result)

        # check token score icx (should be 0)
        balance = get_icx_balance(super(), str(self._irc2_address), self.icon_service)
        self.assertEqual(balance, 0)

        # confirm transaction
        # result = self.confirm_transaction(txuid, from_=self._operator)
        self.confirm_transaction(txuid, from_=self._owner2)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # check getConfirmationCount(should be 2)
        transaction = self.get_transaction(txuid)
        self.assertEqual(len(transaction['confirmations']), 2)

        # check the token score address' icx
        balance = get_icx_balance(super(), str(self._irc2_address), self.icon_service)
        self.assertEqual(balance, 10 * ICX_FACTOR)

        # check multisig wallet score's icx(should be 90)
        balance = get_icx_balance(super(), str(self._transaction_manager), self.icon_service)
        self.assertEqual(balance, 90 * ICX_FACTOR)

        # failure case: when confirming to already executed transaction,
        # transaction shouldn't be executed again.
        self.confirm_transaction(txuid, from_=self._owner3, success=False)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # check the token score address' icx
        balance = get_icx_balance(super(), str(self._irc2_address), self.icon_service)
        self.assertEqual(balance, 10 * ICX_FACTOR)

        # check multisig wallet score's icx(should be 90)
        balance = get_icx_balance(super(), str(self._transaction_manager), self.icon_service)
        self.assertEqual(balance, 90 * ICX_FACTOR)

    def test_send_icx_to_eoa(self):
        result = self.set_wallet_owners_required(2)

        # success case: send icx to eoa (user)
        # deposit 100 icx to wallet SCORE
        self.deposit_icx_to_multisig_score(100 * ICX_FACTOR)

        initial_balance = get_icx_balance(super(), str(self._user.get_address()), self.icon_service)

        # submit transaction which send 10 icx to user
        result = self.msw_transfer_icx(self._user.get_address(), 10 * ICX_FACTOR)
        txuid = self.get_transaction_created_uid(result)

        # check user ICX balance
        balance = get_icx_balance(super(), str(self._user.get_address()), self.icon_service)
        self.assertEqual(balance, initial_balance)

        # confirm transaction
        # result = self.confirm_transaction(txuid, from_=self._operator)
        self.confirm_transaction(txuid, from_=self._owner2)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # check getConfirmationCount(should be 2)
        transaction = self.get_transaction(txuid)
        self.assertEqual(len(transaction['confirmations']), 2)

        # check the user's icx
        balance = get_icx_balance(super(), str(self._user.get_address()), self.icon_service)
        self.assertEqual(balance, initial_balance + 10 * ICX_FACTOR)

        # check multisig wallet score's icx(should be 90)
        balance = get_icx_balance(super(), str(self._transaction_manager), self.icon_service)
        self.assertEqual(balance, 90 * ICX_FACTOR)
