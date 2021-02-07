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


class ABCIconSafe(ABC):
    
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def fallback(self):
        pass

    @abstractmethod
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        pass


class IconSafeProxy(AddressRegistrarProxy):

    NAME = "ICONSAFE_PROXY"
    IconSafeInterface = ProxyScore(ABCIconSafe)

    # ================================================
    #  Fields
    # ================================================
    @property
    def iconsafe(self):
        address = self.registrar.resolve(IconSafeProxy.NAME)
        if not address:
            raise AddressNotInRegistrar(IconSafeProxy.NAME)
        
        return self.create_interface_score(address, IconSafeProxy.IconSafeInterface)

