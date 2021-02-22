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
from ..utility.proxy_score import *


class ABCEventManager(ABC):

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def get_events(self, offset: int = 0) -> list:
        pass


class ABCEventManagerSystemLevel(ABCEventManager):

    @abstractmethod
    def on_add_event(self) -> None:
        pass



class EventManagerProxy(AddressRegistrarProxy):

    NAME = "EVENT_MANAGER_PROXY"
    EventManagerInterface = ProxyScore(ABCEventManagerSystemLevel)

    # ================================================
    #  Fields
    # ================================================
    @property
    def event_manager(self):
        address = self.registrar.resolve(EventManagerProxy.NAME)
        if not address:
            raise AddressNotInRegistrar(EventManagerProxy.NAME)
        return self.create_interface_score(address, EventManagerProxy.EventManagerInterface)


def add_event(func):
    if not isfunction(func):
        raise NotAFunctionError

    @wraps(func)
    def __wrapper(self: object, *args, **kwargs):
        try:
            self.event_manager.on_add_event()
        except AddressNotInRegistrar:
            # Registrar may not be configured yet
            pass
        return func(self, *args, **kwargs)

    return __wrapper
