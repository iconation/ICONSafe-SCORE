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
from contracts.balance_history_manager.consts import ICX_TOKEN_ADDRESS
from tests.utils import *


class TestIntegrateAddressRegistrar(ICONSafeTests):

    def setUp(self):
        super().setUp()

    def test_register(self):
        address = Address.from_string('hx' + 'a'*40)
        name = "test"
        
        # Okay
        self.address_registrar_register(name, address, from_=self._operator)
        resolved = self.address_registrar_resolve(name)
        self.assertTrue(address == resolved)

        # Already Registered
        self.address_registrar_register(name, address, from_=self._operator, success=False)
        resolved = self.address_registrar_resolve(name)
        self.assertTrue(address == resolved)

    def test_resolve(self):
        address = Address.from_string('hx' + 'a'*40)
        name = "test"
        
        # Okay
        self.address_registrar_register(name, address, from_=self._operator)
        resolved = self.address_registrar_resolve(name)
        self.assertTrue(address == resolved)

        # Fill an unknown address
        resolved = self.address_registrar_resolve("unknown")
        self.assertEqual(resolved, None)

    def test_unregister(self):
        address = Address.from_string('hx' + 'a'*40)
        name = "test"

        # Okay
        self.address_registrar_register(name, address, from_=self._operator)
        resolved = self.address_registrar_resolve(name)
        self.assertTrue(address == resolved)

        # Okay
        self.address_registrar_unregister(name, from_=self._operator)
        resolved = self.address_registrar_resolve(name)
        self.assertTrue(resolved == None)

    def test_register_attacker(self):
        address = Address.from_string('hx' + 'a'*40)
        name = "test"
        
        # Not operator
        self.address_registrar_register(name, address, from_=self._attacker, success=False)

    def test_register_already_registered_attacker(self):
        address = Address.from_string('hx' + 'a'*40)
        name = "test"
        
        # Okay
        self.address_registrar_register(name, address, from_=self._operator)
        resolved = self.address_registrar_resolve(name)
        self.assertTrue(address == resolved)

        # Not operator
        self.address_registrar_register(name, address, from_=self._attacker, success=False)

    def test_unregister(self):
        address = Address.from_string('hx' + 'a'*40)
        name = "test"

        # Okay
        self.address_registrar_register(name, address, from_=self._operator)
        resolved = self.address_registrar_resolve(name)
        self.assertTrue(address == resolved)

        # Not operator
        self.address_registrar_unregister(name, from_=self._attacker, success=False)

    def test_reverse_resolve(self):
        address = Address.from_string('hx' + 'a'*40)
        name = "test"
        
        # Okay
        self.address_registrar_register(name, address, from_=self._operator)

        # Already Registered
        reverse_resolved = self.address_registrar_reverse_resolve(address)
        self.assertTrue(name == reverse_resolved)

    def test_resolve_many(self):
        addresses = [Address.from_string('hx' + 'a'*40), Address.from_string('hx' + 'b'*40)]
        names = ["test1", "test2"]
        
        self.address_registrar_register(names[0], addresses[0], from_=self._operator)
        self.address_registrar_register(names[1], addresses[1], from_=self._operator)

        # Okay
        resolved = self.address_registrar_resolve_many(names)
        self.assertTrue(addresses == resolved)

        # Fill an unknown address
        names.append("test3")
        addresses.append(None)
        resolved = self.address_registrar_resolve_many(names)
        self.assertEqual(addresses, resolved)

    def test_reverse_resolve_many(self):
        addresses = [Address.from_string('hx' + 'a'*40), Address.from_string('hx' + 'b'*40)]
        names = ["test1", "test2"]
        self.address_registrar_register(names[0], addresses[0], from_=self._operator)
        self.address_registrar_register(names[1], addresses[1], from_=self._operator)

        # Okay
        resolved = self.address_registrar_reverse_resolve_many(addresses)
        self.assertTrue(names == resolved)

        # Fill an unknown address
        names.append('')
        addresses.append(Address.from_string('hx' + 'c'*40))
        resolved = self.address_registrar_reverse_resolve_many(addresses)
        self.assertEqual(names, resolved)
