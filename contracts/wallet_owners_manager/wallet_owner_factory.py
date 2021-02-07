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

from ..scorelib.id_factory import *
from .wallet_owner import *

class WalletOwnerFactory:

    _NAME = "WALLET_OWNER_FACTORY"

    @staticmethod
    def create(db: IconScoreDatabase, address: Address, name: str) -> int:

        wallet_owner_uid = IdFactory(WalletOwnerFactory._NAME, db).get_uid()

        owner = WalletOwner(wallet_owner_uid, db)

        owner._address.set(address)
        owner._name.set(name)

        return wallet_owner_uid
