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


class TestIntegrateWalletMethod(ICONSafeTests):

    def setUp(self):
        super().setUp()

    def test_only_wallet_execute_method(self):
        # failure case: call method using normal owner
        # all external method which change the state of wallet(e.g. requirement) should be called by own wallet
        change_requirement_params = {"owners_required": "3"}
        change_requirement_tx = transaction_call_error(super(), from_=self._operator,
                                                       to_=self._score_address,
                                                       method="set_wallet_owners_required",
                                                       params=change_requirement_params,
                                                       icon_service=self.icon_service
                                                       )

        add_wallet_owner_params = {"address": str(self._user), "name": "user"}
        add_wallet_owner_tx = transaction_call_error(super(), from_=self._operator,
                                                     to_=self._score_address,
                                                     method="add_wallet_owner",
                                                     params=add_wallet_owner_params,
                                                     icon_service=self.icon_service
                                                     )

        replace_wallet_owner_params = {
            "old_wallet_owner_uid": self.get_wallet_owner_uid(self._operator.get_address()),
            "new_address": str(self._user),
            "new_name": "user"
        }
        replace_wallet_owner_tx = transaction_call_error(super(), from_=self._operator,
                                                         to_=self._score_address,
                                                         method="replace_wallet_owner",
                                                         params=replace_wallet_owner_params,
                                                         icon_service=self.icon_service
                                                         )

        remove_wallet_owner_params = {"wallet_owner_uid": self.get_wallet_owner_uid(self._operator.get_address())}
        remove_wallet_owner_tx = transaction_call_error(super(), from_=self._operator,
                                                        to_=self._score_address,
                                                        method="remove_wallet_owner",
                                                        params=remove_wallet_owner_params,
                                                        icon_service=self.icon_service
                                                        )

        tx_results = [change_requirement_tx, add_wallet_owner_tx, replace_wallet_owner_tx, remove_wallet_owner_tx]

        for tx_result in tx_results:
            self.assertEqual(False, tx_result['status'])

    def test_add_wallet_owner(self):
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)

        # success case: add wallet user successfully
        result = self.add_wallet_owner(self._user.get_address(), "new_owner")

        txuid = self.get_transaction_created_uid(result)

        # confirm transaction
        # self.confirm_transaction(txuid, from_=self._operator)
        self.confirm_transaction(txuid, from_=self._owner2)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # check wallet owners(user should be added)
        owners = self.get_wallet_owners()
        owners = list(map(lambda x: x['address'], owners))
        expected_owners = [self._operator.get_address(), self._owner2.get_address(), self._owner3.get_address(), self._user.get_address()]
        self.assertEqual(expected_owners, owners)

        # failure case: add already exist wallet owner
        result = self.add_wallet_owner(self._operator.get_address(), "operator again")
        txuid = self.get_transaction_created_uid(result)

        # confirm transaction
        # result = self.confirm_transaction(txuid, from_=self._operator)
        result = self.confirm_transaction(txuid, from_=self._owner2)
        txuid, error = self.get_transaction_execution_failure_uid(result)
        self.assertEqual(error, f"IconScoreException('WalletAddressAlreadyExist({self._operator.get_address()})', 0)")

        # check if transaction is not executed
        self.assertEqual("FAILED", self.get_transaction(txuid)['state'])

        # check wallet owners
        owners = self.get_wallet_owners()
        owners = list(map(lambda x: x['address'], owners))
        expected_owners = [self._operator.get_address(), self._owner2.get_address(), self._owner3.get_address(), self._user.get_address()]
        self.assertEqual(expected_owners, owners)

    def test_replace_wallet_owner(self):
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)

        # success case: replace owner successfully(owner3 -> user)
        owner3_uid = self.get_wallet_owner_uid(self._owner3.get_address())
        result = self.replace_wallet_owner(owner3_uid, self._user.get_address(), "user")

        txuid = self.get_transaction_created_uid(result)

        # confirm transaction
        # self.confirm_transaction(txuid, from_=self._operator)
        self.confirm_transaction(txuid, from_=self._owner2)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # check the wallet owner list(should be owner1, owner2, user)
        # check wallet owners
        owners = self.get_wallet_owners()

        owners_address = list(map(lambda x: x['address'], owners))
        expected_owners_address = [self._operator.get_address(), self._owner2.get_address(), self._user.get_address()]
        self.assertEqual(expected_owners_address, owners_address)

        owners_names = list(map(lambda x: x['name'], owners))
        expected_owners_name = ["operator", "owner2", "user"]
        self.assertEqual(expected_owners_name, owners_names)

    def test_replace_wallet_owner_2(self):
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)

        # failure case: try replace wallet owner who is not listed
        unknown_user_uid = 123
        result = self.replace_wallet_owner(unknown_user_uid, self._user.get_address(), "user")
        txuid = self.get_transaction_created_uid(result)

        # result = self.confirm_transaction(txuid, from_=self._operator)
        result = self.confirm_transaction(txuid, from_=self._owner2)
        txuid, error = self.get_transaction_execution_failure_uid(result)
        self.assertEqual(error, f"""IconScoreException("LinkedNodeNotFound('WALLET_OWNERS_MANAGER_wallet_owners_UID_LINKED_LIST_DB', {unknown_user_uid})", 0)""")

        # check if transaction is not executed
        self.assertEqual("FAILED", self.get_transaction(txuid)['state'])

        # check if the wallet owner list is not changed(should be owner1, owner2, owner3)
        owners = self.get_wallet_owners()

        owners_address = list(map(lambda x: x['address'], owners))
        expected_owners_address = [self._operator.get_address(), self._owner2.get_address(), self._owner3.get_address()]
        self.assertEqual(expected_owners_address, owners_address)

    def test_replace_wallet_owner_3(self):
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)

        # failure case: replace owner by operator
        owner3_uid = self.get_wallet_owner_uid(self._owner3.get_address())
        result = self.replace_wallet_owner(owner3_uid, self._operator.get_address(), "operator again")

        txuid = self.get_transaction_created_uid(result)

        # confirm transaction
        # result = self.confirm_transaction(txuid, from_=self._operator)
        result = self.confirm_transaction(txuid, from_=self._owner2)
        txuid, error = self.get_transaction_execution_failure_uid(result)
        self.assertEqual(error, f"IconScoreException('WalletAddressAlreadyExist({self._operator.get_address()})', 0)")

        # check if transaction is not executed
        self.assertEqual("FAILED", self.get_transaction(txuid)['state'])

        # check if the wallet owner list is not changed(should be owner1, owner2, owner3)
        owners = self.get_wallet_owners()
        owners_address = list(map(lambda x: x['address'], owners))
        expected_owners_address = [self._operator.get_address(), self._owner2.get_address(), self._owner3.get_address()]
        self.assertEqual(expected_owners_address, owners_address)

    def test_remove_wallet_owner(self):
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)

        # failure case: try to remove wallet owner who is not listed
        unknown_user_uid = 123
        result = self.remove_wallet_owner(unknown_user_uid)
        txuid = self.get_transaction_created_uid(result)

        # confirm transaction
        # result = self.confirm_transaction(txuid, from_=self._operator)
        result = self.confirm_transaction(txuid, from_=self._owner2)
        txuid, error = self.get_transaction_execution_failure_uid(result)
        self.assertEqual(error, f"""IconScoreException("LinkedNodeNotFound('WALLET_OWNERS_MANAGER_wallet_owners_UID_LINKED_LIST_DB', {unknown_user_uid})", 0)""")

        # check if transaction is not executed
        self.assertEqual("FAILED", self.get_transaction(txuid)['state'])

        # check if the wallet owner list is not changed(should be owner1, owner2, owner3)
        owners = self.get_wallet_owners()
        owners_address = list(map(lambda x: x['address'], owners))
        expected_owners_address = [self._operator.get_address(), self._owner2.get_address(), self._owner3.get_address()]
        self.assertEqual(expected_owners_address, owners_address)

        # success case: remove wallet owner successfully(remove owner3)
        owner3_uid = self.get_wallet_owner_uid(self._owner3.get_address())
        result = self.remove_wallet_owner(owner3_uid)

        txuid_created = self.get_transaction_created_uid(result)

        # confirm transaction
        # result = self.confirm_transaction(txuid_created, from_=self._operator)
        result = self.confirm_transaction(txuid_created, from_=self._owner2)
        self.assertEqual("EXECUTED", self.get_transaction(txuid_created)['state'])

        txuid_executed = self.get_transaction_execution_success_uid(result)
        self.assertEqual(txuid_created, txuid_executed)

        # check the wallet owner list (should be owner1, owner2)
        owners = self.get_wallet_owners()
        owners_address = list(map(lambda x: x['address'], owners))
        expected_owners_address = [self._operator.get_address(), self._owner2.get_address()]
        self.assertEqual(expected_owners_address, owners_address)

        # check the wallet owner3 is not wallet owner
        self.assertEqual(False, self.is_wallet_owner(self._owner3.get_address()))

        # failure case: try to remove wallet owner when owner's count is same as requirement
        # (should not be removed)
        owner2_uid = self.get_wallet_owner_uid(self._owner2.get_address())
        result = self.remove_wallet_owner(owner2_uid)
        txuid = self.get_transaction_created_uid(result)

        # confirm transaction
        # InvalidWalletRequirements(1, 2)
        # result = self.confirm_transaction(txuid, from_=self._operator)
        result = self.confirm_transaction(txuid, from_=self._owner2)
        txuid, error = self.get_transaction_execution_failure_uid(result)
        self.assertEqual(error, f"IconScoreException('InvalidWalletRequirements(1, 2)', 0)")

        # check if transaction is not executed
        self.assertEqual("FAILED", self.get_transaction(txuid)['state'])

        # check the wallet owner list(should be owner1, owner2)
        owners = self.get_wallet_owners()
        owners_address = list(map(lambda x: x['address'], owners))
        expected_owners_address = [self._operator.get_address(), self._owner2.get_address()]
        self.assertEqual(expected_owners_address, owners_address)

    def test_change_requirement(self):
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)

        result = self.set_wallet_owners_required(1)
        txuid = self.get_transaction_created_uid(result)

        # confirm transaction
        # self.confirm_transaction(txuid, from_=self._operator)
        self.confirm_transaction(txuid, from_=self._owner2)

        # check the requirement(should be 1)
        self.assertEqual(1, self.get_wallet_owners_required())

    def test_change_requirement_2(self):
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)

        # failure case: change requirement to 0
        result = self.set_wallet_owners_required(0)
        txuid = self.get_transaction_created_uid(result)

        # confirm transaction
        # result = self.confirm_transaction(txuid, from_=self._operator)
        result = self.confirm_transaction(txuid, from_=self._owner2)
        txuid, error = self.get_transaction_execution_failure_uid(result)
        self.assertEqual(error, f"IconScoreException('InvalidWalletRequirements(3, 0)', 0)")

        # check if transaction is not executed
        self.assertEqual("FAILED", self.get_transaction(txuid)['state'])

        # check the requirement(should be 2)
        self.assertEqual(2, self.get_wallet_owners_required())

    def test_change_requirement_3(self):
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)

        # failure case: try to set requirement more than owners
        result = self.set_wallet_owners_required(4)
        txuid = self.get_transaction_created_uid(result)

        # confirm transaction
        # result = self.confirm_transaction(txuid, from_=self._operator)
        result = self.confirm_transaction(txuid, from_=self._owner2)
        txuid, error = self.get_transaction_execution_failure_uid(result)
        self.assertEqual(error, f"IconScoreException('InvalidWalletRequirements(3, 4)', 0)")

        # check if transaction is not executed
        self.assertEqual("FAILED", self.get_transaction(txuid)['state'])

        # check the requirement(should be 2)
        self.assertEqual(2, self.get_wallet_owners_required())

    def test_change_requirement_execution(self):
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)

        result = self.set_wallet_owners_required(3)
        txuid = self.get_transaction_created_uid(result)

        # confirm transaction
        # self.confirm_transaction(txuid, from_=self._operator)
        self.confirm_transaction(txuid, from_=self._owner2)

        # check the requirement(should be 3)
        self.assertEqual(3, self.get_wallet_owners_required())

        # Create a transaction when the requirement is 3
        result = self.add_wallet_owner(self._user.get_address(), "new_owner")
        add_owner_txuid = self.get_transaction_created_uid(result)

        # confirm transaction by only 2 owners (should still be waiting)
        # self.confirm_transaction(add_owner_txuid, from_=self._operator)
        self.confirm_transaction(add_owner_txuid, from_=self._owner2)
        self.assertEqual("WAITING", self.get_transaction(add_owner_txuid)['state'])

        # Reduce the requirement to 2
        result = self.set_wallet_owners_required(2)
        txuid = self.get_transaction_created_uid(result)

        # confirm transaction
        # self.confirm_transaction(txuid, from_=self._operator)
        self.confirm_transaction(txuid, from_=self._owner2)
        result = self.confirm_transaction(txuid, from_=self._owner3)

        # The add owner should have been executed now
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])
        owners = self.get_wallet_owners()
        owners = list(map(lambda x: x['address'], owners))
        expected_owners = [self._operator.get_address(), self._owner2.get_address(), self._owner3.get_address()]
        self.assertEqual(expected_owners, owners)

    def test_force_cancel_transaction(self):
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)

        result = self.set_wallet_owners_required(3)
        to_be_cancelled_txuid = self.get_transaction_created_uid(result)

        # Only one confirmation
        # self.confirm_transaction(to_be_cancelled_txuid, from_=self._operator)
        self.assertEqual("WAITING", self.get_transaction(to_be_cancelled_txuid)['state'])

        result = self.force_cancel_transaction(to_be_cancelled_txuid)
        txuid = self.get_transaction_created_uid(result)
        # confirm & execute transaction
        # self.confirm_transaction(txuid, from_=self._operator)
        self.confirm_transaction(txuid, from_=self._owner2)
        print(self.get_transaction(txuid))
        self.assertEqual("EXECUTED", self.get_transaction(txuid)['state'])

        # Check if the previous transaction is cancelled
        self.assertEqual("CANCELLED", self.get_transaction(to_be_cancelled_txuid)['state'])
