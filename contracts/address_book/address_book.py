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
from ..scorelib.set import *
from ..scorelib.iterable_dict import *
from ..scorelib.consts import *

from ..interfaces.address_book import *
from ..domain.domain import *

from .consts import *


class AlreadyRegisteredException(Exception):
    pass

class NotRegisteredException(Exception):
    pass


class AddressBook(
    IconScoreBase,
    ABCAddressBook,
    IconScoreMaintenance,
    IconScoreVersion,
    IconScoreExceptionHandler,

    EventManagerProxy
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
        self._address_register = IterableDictDB(f"{AddressBook._NAME}_address_register", self.db, Address, str)
        self._name_register = IterableDictDB(f"{AddressBook._NAME}_name_register", self.db, str, Address)

    @catch_exception
    def on_install(self, registrar_address: Address) -> None:
        super().on_install()
        self.set_registrar_address(registrar_address)
        self.maintenance_disable()
        self.version_update(VERSION)

    @catch_exception
    def on_update(self, registrar_address: Address) -> None:
        super().on_update()

        # if self.is_less_than_target_version('1.0.0'):
        #     self._migrate_v1_0_0()

        self.version_update(VERSION)

    # ================================================
    #  Private methods
    # ================================================
    def __check_name_doesnt_exist(self, name: str) -> None:
        if name in self._address_register:
            raise AlreadyRegisteredException(self._NAME, name)

    def __check_address_doesnt_exist(self, address: Address) -> None:
        if address in self._name_register:
            raise AlreadyRegisteredException(self._NAME, str(address))

    def __check_name_exists(self, name: str) -> None:
        if not (name in self._address_register):
            raise NotRegisteredException(self._NAME, name)

    def __check_address_exists(self, address: Address) -> None:
        if not (address in self._name_register):
            raise NotRegisteredException(self._NAME, str(address))

    # ================================================
    #  External methods
    # ================================================
    @external
    @catch_exception
    @only_iconsafe
    def book_register(self, name: str, address: Address) -> None:
        # --- Checks ---
        # Name:Address bijection
        self.__check_name_doesnt_exist(name)
        self.__check_address_doesnt_exist(address)
        
        # --- OK from here ---
        self._address_register[name] = address
        self._name_register[address] = name

    @external
    @catch_exception
    @only_iconsafe
    def book_unregister(self, name: str) -> None:
        # --- Checks ---
        # Name:Address bijection
        self.__check_name_exists(name)
        address = self._address_register[name]
        self.__check_address_exists(address)

        # --- OK from here ---
        del self._name_register[address]
        del self._address_register[name]

    # ================================================
    #  ReadOnly External methods
    # ================================================
    @external(readonly=True)
    @catch_exception
    def book_resolve(self, name: str) -> Address:
        return self._address_register[name]

    @external(readonly=True)
    @catch_exception
    def book_resolve_many(self, names: List[str]) -> List[Address]:
        return list(map(lambda name: self.book_resolve(name), names[0:MAX_ITERATION_LOOP]))

    @external(readonly=True)
    @catch_exception
    def book_reverse_resolve(self, address: Address) -> str:
        return self._name_register[address]

    @external(readonly=True)
    @catch_exception
    def book_reverse_resolve_many(self, addresses: List[Address]) -> List[str]:
        return list(map(lambda address: self.book_reverse_resolve(address), addresses[0:MAX_ITERATION_LOOP]))
