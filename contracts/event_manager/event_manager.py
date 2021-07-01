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

from ..interfaces.event_manager import *
from ..interfaces.address_registrar import *
from ..interfaces.wallet_settings_manager import *
from ..interfaces.transaction_manager import *
from ..interfaces.balance_history_manager import *
from ..domain.domain import *

from .consts import *


class EventManager(
    IconScoreBase,
    AddressRegistrarProxy,
    IconScoreMaintenance,
    IconScoreVersion,
):

    _NAME = "EVENT_MANAGER"

    # ================================================
    #  Initialization
    # ================================================
    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._events = LinkedListDB(f"{EventManager._NAME}_events", self.db, value_type=bytes)

    def on_install(self, registrar_address: Address) -> None:
        super().on_install()
        self.set_registrar_address(registrar_address)
        self.maintenance_disable()
        self.version_update(VERSION)

    def on_update(self, registrar_address: Address) -> None:
        super().on_update()
        
        # if self.is_less_than_target_version('1.0.0'):
        #     self._migrate_v1_0_0()

        self.version_update(VERSION)

    @external(readonly=True)
    def name(self) -> str:
        return EventManager._NAME

    # ================================================
    #  OnlyDomain External methods
    # ================================================
    @external
    @only_domain
    def on_add_event(self) -> None:
        # Access
        #   - Only addresses registered in the ICONSafe domain
        # Description 
        #   - Add a new event to the event manager
        # Parameters 
        #   - Nothing
        # Returns
        #   - Nothing
        # Throws
        #   - AddressNotInRegistrar
        #   - SenderNotInDomainException

        # A same tx may trigger multiple events
        if len(self._events) > 0 and self._events.head_value() == self.tx.hash:
            return

        if self.tx:  # deploy transaction may not have a txhash yet
            self._events.prepend(self.tx.hash)

    # ================================================
    #  ReadOnly External methods
    # ================================================
    @external(readonly=True)
    def get_events(self, offset: int = 0) -> list:
        return [
            {"uid": event_uid, "hash": event_hash} 
            for event_uid, event_hash in self._events.select(offset)
        ]
