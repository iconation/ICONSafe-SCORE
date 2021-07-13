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

from iconservice import *
from tests.msw_utils import ICONSafeTests
from tests.utils import *
from contracts.transaction_manager.transaction_manager import *


class TestIntegrateReadOnly(ICONSafeTests):

    def setUp(self):
        super().setUp()

    def test_get_transaction_info(self):
        result = self.set_wallet_owners_required(2)

        # waiting transaction
        result = self.set_wallet_owners_required(3)
        txuid = self.get_transaction_created_uid(result)

        # success case: search exist transaction
        transaction = self.get_transaction(txuid)

        self.assertEqual("WAITING", transaction["state"])
        self.assertEqual(1, len(transaction["sub_transactions"]))
        self.assertEqual(str(self._score_address), transaction["sub_transactions"][0]["destination"])
        self.assertEqual("set_wallet_owners_required", transaction["sub_transactions"][0]["method_name"])

        # failure case: try to search not exist transaction(should raise an exception)
        try:
            self.get_transaction(404)
        except Exception as e:
            self.assertEqual("InvalidTransactionType(0)", repr(e))
            
    def test_get_transaction_list_and_get_transaction_count(self):
        self.set_wallet_owners_required(2)

        txcounts = 50

        # success case: get transaction list
        for _ in range(txcounts):
            self.set_wallet_owners_required(3)

        # check wallet_owner who has confirmed transaction
        waiting_txs = self.get_waiting_transactions()
        self.assertEqual(txcounts, len(waiting_txs))

        for transaction in waiting_txs:
            self.assertEqual("WAITING", transaction["state"])
            self.assertEqual(str(self._score_address), transaction["sub_transactions"][0]["destination"])
            self.assertEqual("set_wallet_owners_required", transaction["sub_transactions"][0]["method_name"])

        # success case: get executed transaction list
        executed_txs = self.get_executed_transactions()
        self.assertEqual(1, len(executed_txs))

        transaction = executed_txs[0]
        self.assertEqual("EXECUTED", transaction["state"])
        self.assertEqual(str(self._score_address), transaction["sub_transactions"][0]["destination"])
        self.assertEqual("set_wallet_owners_required", transaction["sub_transactions"][0]["method_name"])

    def test_get_wallet_owners(self):
        owners_wallets = [str(create_address()) for x in range(0, 50)]
        owners = list(map(lambda x: {"address": str(x[1]), "name": str(x[0])}, enumerate(owners_wallets)))
        params = {"registrar_address": self._registrar_address, "owners": owners, "owners_required": "0x2"}

        # deploy multisig wallet which has 50 wallet owners.
        self.unregister("ADDRESS_REGISTRAR_PROXY")
        self.unregister("ICONSAFE_PROXY")
        self.unregister("BALANCE_HISTORY_MANAGER_PROXY")
        self.unregister("EVENT_MANAGER_PROXY")
        self.unregister("TRANSACTION_MANAGER_PROXY")
        self.unregister("WALLET_SETTINGS_MANAGER_PROXY")
        self.unregister("WALLET_OWNERS_MANAGER_PROXY")
        self._wallet_owners_manager = self._deploy_score(self.WALLET_OWNERS_MANAGER_PATH, params=params)['scoreAddress']
        self.register("ADDRESS_REGISTRAR_PROXY", self._registrar_address)
        self.register("ICONSAFE_PROXY", self._score_address)
        self.register("BALANCE_HISTORY_MANAGER_PROXY", self._balance_history_manager)
        self.register("EVENT_MANAGER_PROXY", self._event_manager)
        self.register("TRANSACTION_MANAGER_PROXY", self._transaction_manager)
        self.register("WALLET_SETTINGS_MANAGER_PROXY", self._wallet_settings_manager)
        self.register("WALLET_OWNERS_MANAGER_PROXY", self._wallet_owners_manager)

        # success case: get wallet owners 0 ~ 9, 10 ~ 19, 20 ~ 29, 30 ~ 39, 40 ~ 49
        for x in range(5):
            actual_owners = self.get_wallet_owners(x * 10)[0:10]
            self.assertEqual(len(actual_owners), 10)
            expected_owners = owners[10 * x:]

            for i in range(len(actual_owners)):
                self.assertEqual(expected_owners[i]['name'], actual_owners[i]['name'])

        # success case: exceed owner list(should return owners that does not exceed)
        actual_owners = self.get_wallet_owners(45)
        expected_owners = owners[45:50]

        self.assertEqual(len(actual_owners), 5)
        for i in range(len(actual_owners)):
            self.assertEqual(expected_owners[i]['name'], actual_owners[i]['name'])

    def test_get_confirmations_and_get_confirmation_count(self):
        owners_wallets = [self._operator] + [self._wallet_array[x] for x in range(0, 49)]
        owners = list(map(lambda x: {"address": x[1].get_address(), "name": str(x[0])}, enumerate(owners_wallets)))
        params = {"registrar_address": self._registrar_address, "owners": owners, "owners_required": "50"}

        # deploy multisig wallet which has 50 wallet owners.
        self.unregister("ADDRESS_REGISTRAR_PROXY")
        self.unregister("ICONSAFE_PROXY")
        self.unregister("BALANCE_HISTORY_MANAGER_PROXY")
        self.unregister("EVENT_MANAGER_PROXY")
        self.unregister("TRANSACTION_MANAGER_PROXY")
        self.unregister("WALLET_SETTINGS_MANAGER_PROXY")
        self.unregister("WALLET_OWNERS_MANAGER_PROXY")
        self._wallet_owners_manager = self._deploy_score(self.WALLET_OWNERS_MANAGER_PATH, params=params)['scoreAddress']
        self.register("ADDRESS_REGISTRAR_PROXY", self._registrar_address)
        self.register("ICONSAFE_PROXY", self._score_address)
        self.register("BALANCE_HISTORY_MANAGER_PROXY", self._balance_history_manager)
        self.register("EVENT_MANAGER_PROXY", self._event_manager)
        self.register("TRANSACTION_MANAGER_PROXY", self._transaction_manager)
        self.register("WALLET_SETTINGS_MANAGER_PROXY", self._wallet_settings_manager)
        self.register("WALLET_OWNERS_MANAGER_PROXY", self._wallet_owners_manager)

        # submit transaction by operator
        result = self.set_wallet_owners_required(2)

        # getConfirmationCount should be 1
        txuid = self.get_transaction_confirmed_uid(result)
        transaction = self.get_transaction(txuid)
        self.assertEqual(len(transaction['confirmations']), 1)

        # confirm transaction (odd owners and operator confirm, even owners not confirm)
        for idx, _ in enumerate(owners):
            if idx % 2 == 0:
                continue
            result = self.confirm_transaction(txuid, from_=owners_wallets[idx], success=True)

        transaction = self.get_transaction(txuid)

        owners_uid = [self.get_wallet_owner_uid(self._operator.get_address())]
        owners_uid += [self.get_wallet_owner_uid(owners_wallets[idx].get_address()) for idx, owner in enumerate(owners) if idx % 2 == 1]
        self.assertEqual(transaction['confirmations'], owners_uid)

        # getConfirmationCount should be 26 (submit wallet owner 1 + confirm wallet owner 25)
        self.assertEqual(len(transaction['confirmations']), 25 + 1)

    def test_get_total_number_of_wallet_owner(self):
        result = self.set_wallet_owners_required(2)

        # success case: get total number of wallet owner (should be 3 as default deployed wallet is 3)
        count = self.get_wallet_owners_count()
        self.assertEqual(3, count)

        # success case: after add owner, try get total number of wallet owner (should be 4)
        result = self.add_wallet_owner(self._user.get_address(), "new_owner", success=True)
        txuid = self.get_transaction_created_uid(result)
        # self.confirm_transaction(txuid, from_=self._operator, success=True)
        self.confirm_transaction(txuid, from_=self._owner2, success=True)

        count = self.get_wallet_owners_count()
        self.assertEqual(4, count)

        # success case: after remove owner 3, try get total number of wallet owner (should be 3)
        owner3_uid = self.get_wallet_owner_uid(self._owner3.get_address())
        result = self.remove_wallet_owner(owner3_uid)
        txuid = self.get_transaction_created_uid(result)
        # self.confirm_transaction(txuid, from_=self._operator, success=True)
        self.confirm_transaction(txuid, from_=self._owner2, success=True)

        count = self.get_wallet_owners_count()
        self.assertEqual(3, count)
