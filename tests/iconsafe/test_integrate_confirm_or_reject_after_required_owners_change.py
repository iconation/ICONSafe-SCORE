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


class TestIntegrateConfirmOrRejectAfterRequiredOwnersChange(ICONSafeTests):

    def setUp(self):
        super().setUp()

    def test_integrate_confirm_after_required_owners_change(self):
        # Change owners count to 2
        result = self.set_wallet_owners_required(2)
        txuid = self.get_transaction_execution_success_uid(result)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # Create a single-confirmed transaction (1/2)
        result = self.set_wallet_owners_required(3)
        waiting_txuid = self.get_transaction_created_uid(result)
        self.assertEqual("WAITING", self.get_transaction(waiting_txuid)['state'])

        # Change owners count back to 1 and execute it (2/2)
        result = self.set_wallet_owners_required(1)
        txuid = self.get_transaction_created_uid(result)
        result = self.confirm_transaction(txuid, from_=self._owner2)

        # waiting_txuid should have been executed
        self.assertEqual("EXECUTED", self.get_transaction(waiting_txuid)['state'])
        
    def test_integrate_reject_after_required_owners_change(self):
        # Change owners count to 2
        result = self.set_wallet_owners_required(2)
        txuid = self.get_transaction_execution_success_uid(result)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # Create a single-rejected transaction (1/2)
        result = self.set_wallet_owners_required(3)
        waiting_txuid = self.get_transaction_created_uid(result)
        self.assertEqual("WAITING", self.get_transaction(waiting_txuid)['state'])
        self.revoke_transaction(waiting_txuid)
        self.reject_transaction(waiting_txuid)

        # Change owners count back to 1 and execute it (2/2)
        result = self.set_wallet_owners_required(1)
        txuid = self.get_transaction_created_uid(result)
        result = self.confirm_transaction(txuid, from_=self._owner2)

        # waiting_txuid should have been executed
        self.assertEqual("REJECTED", self.get_transaction(waiting_txuid)['state'])
