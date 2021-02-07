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
from contracts.balance_history_manager.consts import ICX_TOKEN_ADDRESS
from tests.utils import *


class TestIntegrateSubmitTransaction(ICONSafeTests):

    def setUp(self):
        super().setUp()

    def test_balance_history(self):
        # Track the IRC2 token
        result = self.add_balance_tracker(self._irc2_address)

        # Deposit funds to the multisig
        result = self.deposit_icx_to_multisig_score(10000)
        result = self.send_token(10000, self._score_address)

        icx_balance_history = self.get_token_balance_history(ICX_TOKEN_ADDRESS)
        self.assertEqual(len(icx_balance_history), 2)
        self.assertEqual(icx_balance_history[0]['balance'], 10000)

        irc2_balance_history = self.get_token_balance_history(self._irc2_address)
        self.assertEqual(len(irc2_balance_history), 2)
        self.assertEqual(irc2_balance_history[0]['balance'], 10000)

        # Transfer 3000 ICX and 1500 IRC2 to user
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)

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

        # Check the balance history update
        icx_balance_history = self.get_token_balance_history(ICX_TOKEN_ADDRESS)
        self.assertEqual(len(icx_balance_history), 3)
        self.assertEqual(icx_balance_history[0]['balance'], 10000 - 3000)

        irc2_balance_history = self.get_token_balance_history(self._irc2_address)
        self.assertEqual(len(irc2_balance_history), 3)
        self.assertEqual(irc2_balance_history[0]['balance'], 10000 - 1500)
