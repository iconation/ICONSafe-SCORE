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
from ..scorelib.auth import *

class AddressNotInRegistrar(Exception):
    pass

class ABCAddressRegistrar(InterfaceScore):

    @interface
    def name(self) -> str:
        pass

    @interface
    def resolve(self, name: str) -> Address:
        pass

    @interface
    def reverse_resolve(self, address: Address) -> str:
        pass

    @interface
    def resolve_many(self, names: List[str]) -> List[Address]:
        pass

    @interface
    def reverse_resolve_many(self, addresses: List[Address]) -> List[str]:
        pass

    @interface
    def get_owners(self, offset: int = 0) -> list:
        pass

    @interface
    def register(self, name: str, address: Address) -> None:
        pass

    @interface
    def unregister(self, name: str) -> None:
        pass

    @interface
    def add_owner(self, address: Address) -> None:
        pass

    @interface
    def remove_owner(self, address: Address) -> None:
        pass



class AddressRegistrarProxy:

    NAME = "ADDRESS_REGISTRAR_PROXY"

    # ================================================
    #  Fields
    # ================================================
    @property
    def __registrar_address(self) -> VarDB:
        return VarDB(f"{AddressRegistrarProxy.NAME}__registrar_address", self.db, Address)

    @property
    def registrar(self):
        address = self.__registrar_address.get()
        return self.create_interface_score(address, ABCAddressRegistrar)

    # ================================================
    #  Methods
    # ================================================
    @only_owner
    @external
    def set_registrar_address(self, address: Address) -> None:
        self.__registrar_address.set(address)
