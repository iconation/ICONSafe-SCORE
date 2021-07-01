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
from ..scorelib.maintenance import *
from ..scorelib.version import *
from ..scorelib.linked_list import *

from ..interfaces.wallet_owners_manager import *
from ..interfaces.event_manager import *
from ..domain.domain import *

from .wallet_owner import *
from .wallet_owner_factory import *
from .consts import *


class InvalidWalletRequirements(Exception):
    pass


class WalletOwnerDoesntExist(Exception):
    pass


class WalletAddressAlreadyExist(Exception):
    pass


class WalletOwnerDescription(TypedDict):
    address: str
    name: str


class WalletOwnersManager(
    IconScoreBase,
    IconScoreMaintenance,
    IconScoreVersion,

    EventManagerProxy
):
    _NAME = "WALLET_OWNERS_MANAGER"
    _MAX_WALLET_OWNER_COUNT = 100

    # ================================================
    #  Event Logs
    # ================================================
    @add_event
    @eventlog(indexed=1)
    def WalletOwnerAddition(self, wallet_owner_uid: int):
        pass

    @add_event
    @eventlog(indexed=1)
    def WalletOwnerRemoval(self, wallet_owner_uid: int):
        pass

    @add_event
    @eventlog(indexed=1)
    def WalletOwnersRequiredChanged(self, required: int):
        pass

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._wallet_owners = UIDLinkedListDB(f"{WalletOwnersManager._NAME}_wallet_owners", self.db)
        self._address_to_uid_map = DictDB(f"{WalletOwnersManager._NAME}_ADDRESS_TO_UID_MAP", self.db, value_type=int)
        self._wallet_owners_required = VarDB(f"{WalletOwnersManager._NAME}_wallet_owners_required", self.db, value_type=int)

    def on_install(self, registrar_address: Address, owners: List[WalletOwnerDescription], owners_required: int) -> None:
        super().on_install()
        self.set_registrar_address(registrar_address)
        self.maintenance_disable()
        self.version_update(VERSION)
        
        self.__add_many_wallet_owners(owners, owners_required, False)

    def on_update(self, registrar_address: Address, owners: List[WalletOwnerDescription], owners_required: int) -> None:
        super().on_update()

        # if self.is_less_than_target_version('1.0.0'):
        #     self._migrate_v1_0_0()

        self.version_update(VERSION)

    @external(readonly=True)
    def name(self) -> str:
        return WalletOwnersManager._NAME

    # ================================================
    #  Checks
    # ================================================
    def __check_requirements(self, wallet_owner_count: int, owners_required: int):
        if wallet_owner_count > WalletOwnersManager._MAX_WALLET_OWNER_COUNT or owners_required > wallet_owner_count or owners_required <= 0 or wallet_owner_count <= 0:
            raise InvalidWalletRequirements(wallet_owner_count, owners_required)

    def __check_address_doesnt_exist(self, address: Address):
        if self.is_wallet_owner(address):
            raise WalletAddressAlreadyExist(address)

    def __check_exists(self, address: Address) -> None:
        if self._address_to_uid_map[str(address)] == 0:
            raise WalletOwnerDoesntExist(WalletOwnersManager._NAME, str(address))

    # ================================================
    #  Private methods
    # ================================================
    def __add_wallet_owner(self, address: Address, wallet_owner_uid: int, emit_event: bool = True) -> int:
        self._wallet_owners.append(wallet_owner_uid)
        self._address_to_uid_map[str(address)] = wallet_owner_uid
        if emit_event:
            self.WalletOwnerAddition(wallet_owner_uid)

    def __remove_wallet_owner(self, wallet_owner_uid: int) -> int:
        owner = WalletOwner(wallet_owner_uid, self.db)
        self._wallet_owners.remove(wallet_owner_uid)
        self._address_to_uid_map.remove(str(owner._address.get()))
        self.WalletOwnerRemoval(wallet_owner_uid)

    def __add_many_wallet_owners(self, owners: List[WalletOwnerDescription], owners_required: int, emit_event: bool = True):
        # --- Checks ---
        self.__check_requirements(len(owners), owners_required)
        self._wallet_owners_required.set(owners_required)

        for owner in owners:
            address = Address.from_string(owner["address"])
            self.__check_address_doesnt_exist(address)

        # --- OK from here ---
        for owner in owners:
            address, name = Address.from_string(owner["address"]), owner["name"]
            wallet_owner_uid = WalletOwnerFactory.create(self.db, address, name)
            self.__add_wallet_owner(address, wallet_owner_uid, emit_event)

    # ================================================
    #  OnlyIconSafe External methods
    # ================================================
    @only_iconsafe
    @external
    def add_wallet_owner(self, address: Address, name: str) -> None:
        # Access
        #   Only ICONSafe Proxy contract
        # Description 
        #   Add a new owner to the multisig wallet
        # Parameters 
        #   - address : the address of the new owner
        #   - name : the name of the address
        # Returns
        #   - WalletOwnerAddition
        # Throws
        #   - InvalidWalletRequirements (wallet requirements are invalid, such as there are too much wallet owners)
        #   - WalletAddressAlreadyExist (owner already exists)

        # --- Checks ---
        self.__check_requirements(len(self._wallet_owners) + 1, self._wallet_owners_required.get())
        self.__check_address_doesnt_exist(address)
        # --- OK from here ---
        wallet_owner_uid = WalletOwnerFactory.create(self.db, address, name)
        self.__add_wallet_owner(address, wallet_owner_uid)

    @only_iconsafe
    @external
    def remove_wallet_owner(self, wallet_owner_uid: int) -> None:
        # Access
        #   Only ICONSafe Proxy contract
        # Description 
        #   Remove an existing owner to the multisig wallet
        # Parameters 
        #   - wallet_owner_uid: the wallet owner UID
        # Returns
        #   - WalletOwnerRemoval
        # Throws
        #   - InvalidWalletRequirements (wallet requirements are invalid, such as there are too much wallet owners)
        #   - LinkedNodeNotFound (wallet owner UID cannot be found)

        # --- Checks ---
        self.__check_requirements(len(self._wallet_owners) - 1, self._wallet_owners_required.get())

        # --- OK from here ---
        self.__remove_wallet_owner(wallet_owner_uid)

    @only_iconsafe
    @external
    def replace_wallet_owner(self, old_wallet_owner_uid: int, new_address: Address, new_name: str) -> None:
        # Access
        #   Only ICONSafe Proxy contract
        # Description 
        #   Replace an existing owner to the multisig wallet
        # Parameters 
        #   - wallet_owner_uid: the wallet owner UID
        #   - new_address : the new address for the owner
        #   - new_name : the new name for the owner
        # Returns
        #   - Same than WalletOwnersManager.remove_wallet_owner
        #   - Same than WalletOwnersManager.add_wallet_owner
        # Throws
        #   - Same than WalletOwnersManager.remove_wallet_owner
        #   - Same than WalletOwnersManager.add_wallet_owner

        # --- Checks ---
        # Ref: [SlowMist-N01] 
        # The __check_requirements function only check owner numbers. As replace_wallet_owner doesn't change owner numbers, we don't need to check it.
        # self.__check_requirements(len(self._wallet_owners), self._wallet_owners_required.get())

        old_wallet_owner = WalletOwner(old_wallet_owner_uid, self.db)

        # Only the name of the wallet owner may change but the address remain the same.
        # If that's the case, we don't want to raise a duplicate address error.
        if not old_wallet_owner.same_address(new_address):
            self.__check_address_doesnt_exist(new_address)

        # --- OK from here ---
        new_wallet_owner_uid = WalletOwnerFactory.create(self.db, new_address, new_name)
        self.__remove_wallet_owner(old_wallet_owner_uid)
        self.__add_wallet_owner(new_address, new_wallet_owner_uid)

    @only_iconsafe
    @external
    def set_wallet_owners_required(self, owners_required: int) -> None:
        # Access
        #   Only ICONSafe Proxy contract
        # Description 
        #   Change the wallet owners count requirement for transaction execution
        # Parameters 
        #   - owners_required : amount of confirmations / rejections required
        # Returns
        #   - WalletOwnersRequiredChanged
        # Throws
        #   - InvalidWalletRequirements (wallet requirements are invalid, such as there are too much wallet owners)

        # --- Checks ---
        self.__check_requirements(len(self._wallet_owners), owners_required)
        # --- OK from here ---
        self._wallet_owners_required.set(owners_required)
        self.WalletOwnersRequiredChanged(owners_required)

    # ================================================
    #  ReadOnly External methods
    # ================================================
    @external(readonly=True)
    def get_wallet_owners(self, offset: int = 0) -> list:
        return [self.get_wallet_owner(wallet_owner_uid) for wallet_owner_uid in self._wallet_owners.select(offset)]

    @external(readonly=True)
    def get_wallet_owner(self, wallet_owner_uid: int) -> dict:
        return WalletOwner(wallet_owner_uid, self.db).serialize()

    @external(readonly=True)
    def get_wallet_owner_uid(self, address: Address) -> int:
        self.__check_exists(address)
        return self._address_to_uid_map[str(address)]

    @external(readonly=True)
    def get_wallet_owners_count(self) -> int:
        return len(self._wallet_owners)

    @external(readonly=True)
    def is_wallet_owner(self, address: Address) -> bool:
        return self._address_to_uid_map[str(address)] != 0

    @external(readonly=True)
    def get_wallet_owners_required(self) -> int:
        return self._wallet_owners_required.get()
