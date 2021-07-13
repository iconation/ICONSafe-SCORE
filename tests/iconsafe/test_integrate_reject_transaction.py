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

ICX_FACTOR = 10 ** 18


class TestIntegrateRejectTransaction(ICONSafeTests):

    def setUp(self):
        super().setUp()

    def test_reject_transaction_success(self):
        # success case: valid params format
        result = self.set_wallet_owners_required(2)

        txuid = self.get_transaction_execution_success_uid(result)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # deposit 100 icx to wallet SCORE
        self.deposit_icx_to_multisig_score(100 * ICX_FACTOR)

        # submit transaction which send 10 icx to token score
        result = self.msw_transfer_icx(self._irc2_address, 10 * ICX_FACTOR)
        txuid = self.get_transaction_created_uid(result)

        # Reject transaction
        result = self.reject_transaction(txuid, from_=self._owner2)
        self.assertEqual(self.get_transaction_rejected_uid(result), txuid)

        result = self.reject_transaction(txuid, from_=self._owner3)
        self.assertEqual(self.get_transaction_rejected_uid(result), txuid)

        self.assertEqual(self.get_transaction_rejection_success_uid(result), txuid)

        self.assertEqual("REJECTED", self.get_transaction(txuid)['state'])

    def test_reject_transaction_change_mind_success(self):
        # success case: valid params format
        result = self.set_wallet_owners_required(3)

        txuid = self.get_transaction_execution_success_uid(result)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # deposit 100 icx to wallet SCORE
        self.deposit_icx_to_multisig_score(100 * ICX_FACTOR)

        # submit transaction which send 10 icx to token score
        result = self.msw_transfer_icx(self._irc2_address, 10 * ICX_FACTOR)
        txuid = self.get_transaction_created_uid(result)
        # self.confirm_transaction(txuid, from_=self._operator)

        # Reject transaction
        result = self.reject_transaction(txuid, from_=self._owner2)
        self.assertEqual(self.get_transaction_rejected_uid(result), txuid)

        result = self.reject_transaction(txuid, from_=self._owner3)
        self.assertEqual(self.get_transaction_rejected_uid(result), txuid)

        result = self.revoke_transaction(txuid, from_=self._operator)
        self.assertEqual(self.get_transaction_revoked_uid(result), txuid)

        result = self.reject_transaction(txuid, from_=self._operator)
        self.assertEqual(self.get_transaction_rejection_success_uid(result), txuid)

        self.assertEqual("REJECTED", self.get_transaction(txuid)['state'])
