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


class TestIntegrateSubmitTransaction(ICONSafeTests):
    def setUp(self):
        super().setUp()

    def test_submit_transaction_validate_params_format(self):
        # success case: valid params format
        result = self.set_wallet_owners_required(2)
        # result = self.confirm_transaction_created(result)
        txuid = self.get_transaction_execution_success_uid(result)
        self.assertEqual("EXECUTED", self.get_transaction(txuid)["state"])

        # failure case: when type and value's actual type is not match, should be revert.
        not_match_type_params = [{"name": "owners_required", "type": "bool", "value": "521"}]

        result = self.set_wallet_owners_required(params=not_match_type_params, success=False)
        self.assertEqual("Invalid bool value", result["failure"]["message"])

        # failure case: when input unsupported type as params' type
        unsupported_type_params = [{"name": "owners_required", "type": "dict", "value": "{'test':'test'}"}]
        result = self.set_wallet_owners_required(params=unsupported_type_params, success=False)
        expected_revert_massage = (
            "dict is not supported type (only dict_keys(['int', 'str', 'bool', 'Address', 'bytes', 'List', 'TypedDict']) are supported)"
        )
        actual_revert_massage = result["failure"]["message"]
        self.assertEqual(expected_revert_massage, actual_revert_massage)

        # failure case: invalid json format
        invalid_json_format_params = "{'test': }"
        result = self.set_wallet_owners_required(params=invalid_json_format_params, success=False)
        expected_revert_massage = "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)"
        actual_revert_massage = result["failure"]["message"]
        self.assertEqual(expected_revert_massage, actual_revert_massage)

    def test_submit_transaction_check_wallet_owner(self):
        # failure case: not included wallet owner
        result = self.set_wallet_owners_required(2, from_=self._attacker, success=False)
        expected_revert_massage = f"{self._attacker.get_address()}"
        actual_revert_massage = result["failure"]["message"]
        self.assertEqual(expected_revert_massage, actual_revert_massage)

    def test_submit_transaction_check_transaction_list(self):
        # success case: submit 4 transaction and one transaction will be failed
        # transaction total count should be 3
        invalid_params = [{"name": "owners_required", "type": "dict", "value": "{'test':'test'}"}]

        tx_results = []

        tx_results.append(self.set_wallet_owners_required(2))
        tx_results.append(self.set_wallet_owners_required(2))
        tx_results.append(self.set_wallet_owners_required(params=invalid_params, success=False))
        tx_results.append(self.set_wallet_owners_required(2))

        self.assertEqual(True, tx_results[0]["status"])
        self.assertEqual(True, tx_results[1]["status"])
        self.assertEqual(False, tx_results[2]["status"])
        self.assertEqual(True, tx_results[3]["status"])

        # check executed transaction count (should be 1, the first 1->2 req change)
        executed_transaction = self.get_executed_transactions_count()
        self.assertEqual(1, executed_transaction)

        # check waiting transaction count (should be 2, the two valid transactions after the req change)
        waiting_transaction = self.get_waiting_transactions_count()
        self.assertEqual(2, waiting_transaction)
