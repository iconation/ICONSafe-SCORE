# -*- coding: utf-8 -*-

# Copyright 2021 ICONation
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

from iconservice import *
from .address_registrar import *

class ABCAddressBook(InterfaceScore):

    @interface
    def name(self) -> str:
        pass

    @interface
    def book_register(self, name: str, address: Address) -> None:
        pass

    @interface
    def book_unregister(self, name: str) -> None:
        pass

    @interface
    def book_resolve(self, name: str) -> Address:
        pass

    @interface
    def book_reverse_resolve(self, address: Address) -> str:
        pass

    @interface
    def book_resolve_many(self, names: List[str]) -> List[Address]:
        pass

    @interface
    def book_reverse_resolve_many(self, addresses: List[Address]) -> List[str]:
        pass


class AddressBookProxy(AddressRegistrarProxy):

    NAME = "ADDRESS_BOOK_PROXY"

    # ================================================
    #  Fields
    # ================================================
    @property
    def address_book(self):
        address = self.registrar.resolve(AddressBookProxy.NAME)
        if not address:
            raise AddressNotInRegistrar(AddressBookProxy.NAME)

        return self.create_interface_score(address, ABCAddressBook)
