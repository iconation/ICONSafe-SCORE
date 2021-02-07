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


class TestIntegrateCancelTransaction(ICONSafeTests):

    def setUp(self):
        super().setUp()

    def test_cancel_transaction(self):
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)

        txuid_executed = self.get_transaction_confirmed_uid(result)

        # submit transaction
        result = self.set_wallet_owners_required(3)
        # result = self.confirm_transaction_created(result)
        txuid = self.get_transaction_confirmed_uid(result)

        # failure case: cancel with confirmed transaction
        result = self.cancel_transaction(txuid, success=False)
        expected_revert_massage = f"OutgoingTransactionHasParticipation('TRANSACTION_{txuid}')"
        self.assertEqual(expected_revert_massage, result['failure']['message'])
        self.assertEqual("WAITING", self.get_transaction(txuid)['state'])

        # success case: Submit -> Confirm -> Revoke -> Cancel using confirmed wallet owner
        result = self.set_wallet_owners_required(3)
        # result = self.confirm_transaction_created(result)
        txuid = self.get_transaction_confirmed_uid(result)
        result = self.revoke_transaction(txuid)
        result = self.cancel_transaction(txuid)
        txuid = self.get_transaction_cancelled_uid(result)
        self.assertEqual("CANCELLED", self.get_transaction(txuid)['state'])
        self.assertEqual(len(self.get_transaction(txuid)['confirmations']), 0)

        # success case: Submit -> Unconfirm -> Cancel using confirmed wallet owner
        result = self.set_wallet_owners_required(3)
        txuid = self.get_transaction_created_uid(result)
        self.revoke_transaction(txuid, from_=self._operator)
        result = self.cancel_transaction(txuid)
        txuid = self.get_transaction_cancelled_uid(result)
        self.assertEqual("CANCELLED", self.get_transaction(txuid)['state'])

        # success case: cancel using any wallet owner
        result = self.set_wallet_owners_required(3)
        txuid = self.get_transaction_created_uid(result)
        self.revoke_transaction(txuid)
        result = self.cancel_transaction(txuid, from_=self._owner2)
        txuid = self.get_transaction_cancelled_uid(result)
        self.assertEqual("CANCELLED", self.get_transaction(txuid)['state'])

        # failure case: cancel using not wallet owner
        result = self.set_wallet_owners_required(3)
        txuid = self.get_transaction_created_uid(result)
        result = self.cancel_transaction(txuid, from_=self._attacker, success=False)
        owner2_uid = self.get_wallet_owner_uid(self._owner2.get_address())
        expected_revert_massage = f"SenderNotMultisigOwnerError({self._attacker.get_address()})"
        self.assertEqual(expected_revert_massage, result['failure']['message'])

        # failure case: try cancel transaction which is already executed
        transaction = self.get_transaction(txuid_executed)
        self.assertEqual(transaction['state'], 'EXECUTED')
        result = self.cancel_transaction(txuid_executed, success=False)
        expected_revert_massage = f"InvalidState('OUTGOING_TRANSACTION_{txuid_executed}_state_STATEDB', 'EXECUTED', 'WAITING')"
        self.assertEqual(expected_revert_massage, result['failure']['message'])
