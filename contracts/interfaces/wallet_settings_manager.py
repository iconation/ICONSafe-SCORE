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


class ABCWalletSettingsManager(InterfaceScore):
    @interface
    def name(self) -> str:
        pass

    @interface
    def get_safe_name(self) -> str:
        pass

    @interface
    def set_safe_name(self, safe_name: str) -> None:
        pass


class WalletSettingsManagerProxy(AddressRegistrarProxy):

    NAME = "WALLET_SETTINGS_MANAGER_PROXY"
    WalletSettingsManagerInterface = ABCWalletSettingsManager

    # ================================================
    #  Fields
    # ================================================
    @property
    def wallet_settings_manager(self):
        address = self.registrar.resolve(WalletSettingsManagerProxy.NAME)
        if not address:
            raise AddressNotInRegistrar(WalletSettingsManagerProxy.NAME)
        
        return self.create_interface_score(address, ABCWalletSettingsManager)

