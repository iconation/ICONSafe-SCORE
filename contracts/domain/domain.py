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

from ..interfaces.event_manager import *
from ..interfaces.address_registrar import *
from ..interfaces.address_book import *
from ..interfaces.wallet_owners_manager import *
from ..interfaces.iconsafe import *
from ..interfaces.transaction_manager import *
from ..interfaces.balance_history_manager import *
from ..interfaces.wallet_settings_manager import *


class SenderNotInDomainException(Exception):
    pass


class SenderNotIconSafeException(Exception):
    pass


class SenderNotTransactionManagerException(Exception):
    pass

DOMAIN_NAMES = [
    AddressRegistrarProxy.NAME,
    AddressBookProxy.NAME,
    BalanceHistoryManagerProxy.NAME,
    EventManagerProxy.NAME,
    IconSafeProxy.NAME,
    TransactionManagerProxy.NAME,
    WalletOwnersManagerProxy.NAME,
    WalletSettingsManagerProxy.NAME,
]

def only_domain(func):
    if not isfunction(func):
        raise NotAFunctionError

    @wraps(func)
    def __wrapper(self: object, *args, **kwargs):

        domain = self.registrar.resolve_many(DOMAIN_NAMES)
        
        if None in domain:
            raise AddressNotInRegistrar(', '.join(DOMAIN_NAMES))

        if not self.msg.sender in domain:
            raise SenderNotInDomainException(self.msg.sender)

        return func(self, *args, **kwargs)

    return __wrapper


def only_iconsafe(func):
    if not isfunction(func):
        raise NotAFunctionError

    @wraps(func)
    def __wrapper(self: object, *args, **kwargs):

        name = IconSafeProxy.NAME
        iconsafe = self.registrar.resolve(name)
        if not iconsafe:
            raise AddressNotInRegistrar(name)

        if self.msg.sender != iconsafe:
            raise SenderNotIconSafeException(self.msg.sender)

        return func(self, *args, **kwargs)

    return __wrapper


def only_transaction_manager(func):
    if not isfunction(func):
        raise NotAFunctionError

    @wraps(func)
    def __wrapper(self: object, *args, **kwargs):

        name = TransactionManagerProxy.NAME
        transaction_manager = self.registrar.resolve(name)
        if not transaction_manager:
            raise AddressNotInRegistrar(name)

        if self.msg.sender != transaction_manager:
            raise SenderNotTransactionManagerException(self.msg.sender)

        return func(self, *args, **kwargs)

    return __wrapper
