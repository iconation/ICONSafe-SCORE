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


class ABCWalletOwnersManager(InterfaceScore):

    @interface
    def name(self) -> str:
        pass

    @interface
    def add_wallet_owner(self, address: Address, name: str) -> None:
        pass

    @interface
    def remove_wallet_owner(self, wallet_owner_uid: int) -> None:
        pass

    @interface
    def replace_wallet_owner(self, old_wallet_owner_uid: int, new_address: Address, new_name: str) -> None:
        pass

    @interface
    def set_wallet_owners_required(self, owners_required: int) -> None:
        pass

    @interface
    def get_wallet_owners(self, offset: int = 0) -> list:
        pass

    @interface
    def get_wallet_owner(self, wallet_owner_uid: int) -> dict:
        pass

    @interface
    def get_wallet_owner_uid(self, address: Address) -> int:
        pass

    @interface
    def get_wallet_owners_count(self) -> int:
        pass

    @interface
    def is_wallet_owner(self, address: Address) -> bool:
        pass

    @interface
    def get_wallet_owners_required(self) -> int:
        pass


class WalletOwnersManagerProxy(AddressRegistrarProxy):

    NAME = "WALLET_OWNERS_MANAGER_PROXY"

    # ================================================
    #  Fields
    # ================================================
    @property
    def wallet_owners_manager(self):
        address = self.registrar.resolve(WalletOwnersManagerProxy.NAME)
        if not address:
            raise AddressNotInRegistrar(WalletOwnersManagerProxy.NAME)
        
        return self.create_interface_score(address, ABCWalletOwnersManager)


class SenderNotMultisigOwnerError(Exception):
    pass


def only_multisig_owner(func):
    if not isfunction(func):
        revert('NotAFunctionError')

    @wraps(func)
    def __wrapper(self: object, *args, **kwargs):
        if not self.wallet_owners_manager.is_wallet_owner(self.msg.sender):
            raise SenderNotMultisigOwnerError(self.msg.sender)

        return func(self, *args, **kwargs)

    return __wrapper
