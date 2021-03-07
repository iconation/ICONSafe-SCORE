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

from ..interfaces.wallet_settings_manager import *
from ..interfaces.event_manager import *
from ..interfaces.wallet_owners_manager import *
from ..domain.domain import *

from .consts import *

class WalletSettingsManager(
    IconScoreBase,
    ABCWalletSettingsManager,
    IconScoreMaintenance,
    IconScoreVersion,
    IconScoreExceptionHandler,

    EventManagerProxy,
    WalletOwnersManagerProxy
):
    _NAME = "WALLET_SETTINGS_MANAGER"

    # ================================================
    #  Event Logs
    # ================================================
    @add_event
    @eventlog
    def WalletSettingsSafeNameChanged(self, safe_name: str):
        pass

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._safe_name = VarDB(f"{WalletSettingsManager._NAME}_safe_name", self.db, value_type=str)

    @catch_exception
    def on_install(self, registrar_address: Address) -> None:
        super().on_install()
        self.set_registrar_address(registrar_address)
        self.maintenance_disable()
        self.version_update(VERSION)
        
        self._safe_name.set(DEFAULT_SAFENAME)

    @catch_exception
    def on_update(self, registrar_address: Address) -> None:
        super().on_update()

        # if self.is_less_than_target_version('1.0.0'):
        #     self._migrate_v1_0_0()

        self.version_update(VERSION)

    @external(readonly=True)
    def name(self) -> str:
        return WalletSettingsManager._NAME

    # ================================================
    #  External methods
    # ================================================
    @external(readonly=True)
    def get_safe_name(self) -> str:
        return self._safe_name.get()

    @external
    @only_iconsafe
    def set_safe_name(self, safe_name: str) -> None:
        # Access
        #   Only ICONSafe Proxy contract
        # Description 
        #   Change the safe name
        # Parameters 
        #   - safe_name : the new safe name
        # Returns
        #   - WalletSettingsSafeNameChanged
        # Throws
        #   Nothing

        self._safe_name.set(safe_name)
        self.WalletSettingsSafeNameChanged(safe_name)
