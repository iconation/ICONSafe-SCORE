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


class TestIntegrateSubmitSubTransaction(ICONSafeTests):

    def setUp(self):
        super().setUp()

    def test_multiple_sub_transactions(self):
        self.deposit_icx_to_multisig_score(10000)
        self.send_token(10000, self._score_address)

        # success case: transfer 3000 ICX and 1500 IRC2 to user
        result = self.set_wallet_owners_required(2)
        txuid = self.get_transaction_execution_success_uid(result)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        initial_icx_balance = get_icx_balance(super(), str(self._user.get_address()), self.icon_service)
        initial_irc2_balance = self.balance_token(self._user.get_address())

        sub_transactions = []
        sub_transactions.append(self.msw_transfer_icx_params(self._user.get_address(), 1000))
        sub_transactions.append(self.msw_transfer_icx_params(self._user.get_address(), 2000))
        sub_transactions.append(self.msw_transfer_irc2_params(self._irc2_address, self._user.get_address(), 500))
        sub_transactions.append(self.msw_transfer_irc2_params(self._irc2_address, self._user.get_address(), 1000))

        result = self.submit_transaction(self._operator, sub_transactions)
        txuid = self.get_transaction_created_uid(result)

        # result = self.confirm_transaction(txuid, self._operator)
        result = self.confirm_transaction(txuid, self._owner2)
        txuid = self.get_transaction_execution_success_uid(result)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # Check new updated ICX balance
        new_icx_balance = get_icx_balance(super(), str(self._user.get_address()), self.icon_service)
        self.assertEqual(new_icx_balance, initial_icx_balance + 3000)

        # Check new updated IRC2 balance
        new_irc2_balance = self.balance_token(self._user.get_address())
        self.assertEqual(new_irc2_balance, initial_irc2_balance + 1500)

    def test_multiple_sub_transactions_must_be_atomic(self):
        self.deposit_icx_to_multisig_score(10000)

        result = self.set_wallet_owners_required(2)
        txuid = self.get_transaction_execution_success_uid(result)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        initial_icx_balance = get_icx_balance(super(), str(self._user.get_address()), self.icon_service)

        # The 2 first transactions should work, but the third one raises an out of balance
        # exception. All transactions must be rollbacked.
        sub_transactions = []
        sub_transactions.append(self.msw_transfer_icx_params(self._user.get_address(), 1000))
        sub_transactions.append(self.msw_transfer_icx_params(self._user.get_address(), 2000))
        sub_transactions.append(self.msw_transfer_icx_params(self._user.get_address(), 10000000))

        result = self.submit_transaction(self._operator, sub_transactions)
        txuid = self.get_transaction_created_uid(result)

        # Check if transaction failed
        # result = self.confirm_transaction(txuid, self._operator)
        result = self.confirm_transaction(txuid, self._owner2)
        self.assertEqual("FAILED", self.get_transaction(txuid)['state'])

        # Check if rollbacked
        new_icx_balance = get_icx_balance(super(), str(self._user.get_address()), self.icon_service)
        self.assertEqual(new_icx_balance, initial_icx_balance)
