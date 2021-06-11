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


# SCORELib

scorelib_bag = [
    "scorelib/__init__.py",
    "scorelib/consts.py",
    "scorelib/bag.py",
]

scorelib_set = [
    "scorelib/__init__.py",
    *scorelib_bag,
    "scorelib/set.py",
]

scorelib_consts = [
    "scorelib/__init__.py",
    "scorelib/consts.py",
]

scorelib_utils = [
    "scorelib/__init__.py",
    *scorelib_consts,
    "scorelib/utils.py",
]

scorelib_state = [
    "scorelib/__init__.py",
    *scorelib_utils,
    "scorelib/state.py",
]

scorelib_iterabledict = [
    "scorelib/__init__.py",
    *scorelib_set,
    "scorelib/consts.py",
    "scorelib/iterable_dict.py",
]

scorelib_id_factory = [
    "scorelib/__init__.py",
    "scorelib/id_factory.py",
]

scorelib_linkedlist = [
    "scorelib/__init__.py",
    *scorelib_id_factory,
    "scorelib/consts.py",
    "scorelib/linked_list.py",
]

scorelib_exception = [
    "scorelib/__init__.py",
    "scorelib/exception.py",
]

scorelib_auth = [
    "scorelib/__init__.py",
    "scorelib/auth.py",
]

scorelib_version = [
    "scorelib/__init__.py",
    "scorelib/version.py",
]

scorelib_maintenance = [
    "scorelib/__init__.py",
    *scorelib_exception,
    *scorelib_auth,
    *scorelib_utils,
    *scorelib_state,
    "scorelib/maintenance.py",
]

scorelib_base = [
    "scorelib/__init__.py",
    *scorelib_exception,
    *scorelib_maintenance,
    *scorelib_utils,
    *scorelib_version,
]


# ICONSafe interfaces
proxy_score = [
    "utility/__init__.py",
    "utility/proxy_score.py",
]

interface_address_registrar = [
    "interfaces/__init__.py",
    *proxy_score,
    *scorelib_exception,
    *scorelib_auth,
    "interfaces/address_registrar.py",
]

interface_balance_history_manager = [
    "interfaces/__init__.py",
    *interface_address_registrar,
    *proxy_score,
    "interfaces/balance_history_manager.py",
]

interface_wallet_owners_manager = [
    "interfaces/__init__.py",
    *interface_address_registrar,
    *proxy_score,
    "interfaces/wallet_owners_manager.py",
]

interface_event_manager = [
    "interfaces/__init__.py",
    *interface_address_registrar,
    *proxy_score,
    "interfaces/event_manager.py",
]

interface_transaction_manager = [
    "interfaces/__init__.py",
    *interface_address_registrar,
    *proxy_score,
    "interfaces/transaction_manager.py",
]

interface_address_book = [
    "interfaces/__init__.py",
    *interface_address_registrar,
    *proxy_score,
    "interfaces/address_book.py",
]

interface_wallet_settings_manager = [
    "interfaces/__init__.py",
    *interface_address_registrar,
    *proxy_score,
    "interfaces/wallet_settings_manager.py",
]

interface_iconsafe = [
    "interfaces/__init__.py",
    *interface_address_registrar,
    *proxy_score,
    "interfaces/iconsafe.py",
]

interface_irc2 = [
    "interfaces/__init__.py",
    "interfaces/irc2.py",
]

consts_balance_history_manager = [
    "balance_history_manager/__init__.py",
    "balance_history_manager/consts.py",
]

# ICONSafe objects
domain = [
    "domain/__init__.py",
    *interface_event_manager,
    *interface_address_registrar,
    *interface_address_book,
    *interface_wallet_owners_manager,
    *interface_iconsafe,
    *interface_transaction_manager,
    *interface_balance_history_manager,
    *interface_wallet_settings_manager,
    "domain/domain.py",
]

type_converter = [
    "type_converter/__init__.py",
    "type_converter/type_converter.py",
]


# transaction_manager
transaction = [
    *scorelib_state,
]

outgoing_transaction = [
    *scorelib_set,
    *scorelib_state,
]

incoming_transaction = [
    *scorelib_id_factory,
    *type_converter,
]

transaction_factory = [
    *scorelib_id_factory,
    *outgoing_transaction,
    *incoming_transaction,
]

# balance_history
balance_history = [
    *scorelib_id_factory,
]

# wallet_owner
wallet_owner = [
]

wallet_owner_factory = [
    *scorelib_id_factory,
    *wallet_owner,
]

config = {
    "address_book": [
        *scorelib_base,
        *scorelib_iterabledict,
        *scorelib_consts,
        *interface_address_book,
        *domain,
    ],
    "address_registrar": [
        *scorelib_base,
        *scorelib_set,
        *scorelib_iterabledict,
        *scorelib_consts,
        *interface_address_registrar,
    ],
    "balance_history_manager": [
        *scorelib_base,
        *scorelib_set,
        *scorelib_linkedlist,
        *interface_balance_history_manager,
        *interface_transaction_manager,
        *interface_event_manager,
        *interface_irc2,
        *domain,
        *balance_history,
    ],
    "event_manager": [
        *scorelib_base,
        *interface_event_manager,
        *interface_address_registrar,
        *interface_wallet_settings_manager,
        *interface_transaction_manager,
        *interface_balance_history_manager,
        *scorelib_linkedlist,
        *domain,
    ],
    "transaction_manager": [
        *scorelib_base,
        *scorelib_linkedlist,
        *interface_transaction_manager,
        *interface_balance_history_manager,
        *interface_wallet_owners_manager,
        *interface_event_manager,
        *domain,
        *consts_balance_history_manager,
        *transaction,
        *transaction_factory,
    ],
    "wallet_owners_manager": [
        *scorelib_base,
        *scorelib_linkedlist,
        *interface_wallet_owners_manager,
        *interface_event_manager,
        *domain,
        *wallet_owner,
        *wallet_owner_factory,
    ],
    "wallet_settings_manager": [
        *scorelib_base,
        *interface_wallet_settings_manager,
        *interface_event_manager,
        *interface_wallet_owners_manager,
        *domain,
    ],
    "iconsafe": [
        *scorelib_base,
        *interface_iconsafe,
        *interface_transaction_manager,
        *interface_balance_history_manager,
        *interface_wallet_owners_manager,
        *interface_event_manager,
        *interface_wallet_settings_manager,
        *interface_address_book,
        *interface_irc2,
        *consts_balance_history_manager,
        *domain,
    ]
}

# Remove duplicates
for package_name, deps in config.items():
    config[package_name] = list(set(deps))