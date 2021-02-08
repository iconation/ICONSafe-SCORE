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
from ..scorelib.exception import *
from ..scorelib.maintenance import *
from ..scorelib.version import *
from ..scorelib.auth import *
from ..scorelib.set import *
from ..scorelib.iterable_dict import *

from ..interfaces.address_registrar import *

from .consts import *

class SenderIsNotOwner(Exception):
    pass


class AddressRegistrar(
    IconScoreBase,
    ABCAddressRegistrar,
    IconScoreMaintenance,
    IconScoreVersion,
    IconScoreExceptionHandler,
):
    _NAME = "ADDRESS_REGISTRAR"

    # ================================================
    #  Event Logs
    # ================================================

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._owners = SetDB(f"{AddressRegistrar._NAME}_owners", self.db, Address)
        self._address_register = IterableDictDB(f"{AddressRegistrar._NAME}_address_register", self.db, Address, str)
        self._name_register = IterableDictDB(f"{AddressRegistrar._NAME}_name_register", self.db, str, Address)

    @catch_exception
    def on_install(self) -> None:
        super().on_install()
        self.maintenance_disable()
        self.version_update(VERSION)
        
        self.add_owner(self.msg.sender)
        self.register(AddressRegistrarProxy.NAME, self.address)

    @catch_exception
    def on_update(self) -> None:
        super().on_update()

        # if self.is_less_than_target_version('1.0.0'):
        #     self._migrate_v1_0_0()

        self.version_update(VERSION)

    # ================================================
    #  Private methods
    # ================================================
    def __check_owner(self, address: Address) -> None:
        if not address in self._owners:
            raise SenderIsNotOwner(AddressRegistrar._NAME)

    # ================================================
    #  External methods
    # ================================================
    @external
    @catch_exception
    def register(self, name: str, address: Address) -> None:
        self.__check_owner(self.msg.sender)
        self._address_register[name] = address
        self._name_register[address] = name

    @external
    @catch_exception
    def unregister(self, name: str) -> None:
        self.__check_owner(self.msg.sender)
        address = self._address_register[name]
        del self._name_register[address]
        del self._address_register[name]

    @external(readonly=True)
    @catch_exception
    def resolve(self, name: str) -> Address:
        return self._address_register[name]

    @external(readonly=True)
    @catch_exception
    def resolve_many(self, names: List[str]) -> List[Address]:
        result = []
        for name in names:
            result.append(self._address_register[name])
        return result

    @external(readonly=True)
    @catch_exception
    def reverse_resolve(self, address: Address) -> str:
        return self._name_register[address]

    @external(readonly=True)
    @catch_exception
    def reverse_resolve_many(self, addresses: List[Address]) -> List[str]:
        result = []
        for address in addresses:
            result.append(self._name_register[address])
        return result

    # --- Owners management ---
    @external
    @catch_exception
    @only_owner
    def add_owner(self, address: Address) -> None:
        self._owners.add(address)

    @external
    @catch_exception
    @only_owner
    def remove_owner(self, address: Address) -> None:
        self._owners.remove(address)

    @external(readonly=True)
    @catch_exception
    def get_owners(self, offset: int = 0) -> list:
        return self._owners.select(offset)
