# -*- coding: utf-8 -*-

# Copyright 2020 ICONation
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
from .bag import *


class SetDB(BagDB):
    _NAME = '_SETDB'

    def __init__(self, var_key: str, db: IconScoreDatabase, value_type: type, order=False):
        name = var_key + SetDB._NAME
        super().__init__(name, db, value_type, order)
        self._name = name
        self._db = db

    def add(self, item) -> None:
        if item not in self._items:
            super().add(item)

    def remove(self, item) -> None:
        if item not in self._items:
            raise ItemNotFound(self._name, str(item))
        super().remove(item)

    def discard(self, item) -> None:
        if item in self._items:
            super().remove(item)

    def pop(self):
        return self._items.pop()

    def difference(self, other: set):
        return self._to_set().difference(other)

    def intersection(self, other: set):
        return self._to_set().intersection(other)

    def isdisjoint(self, other: set) -> bool:
        return self._to_set().isdisjoint(other)

    def issubset(self, other: set) -> bool:
        return self._to_set().issubset(other)

    def issuperset(self, other: set) -> bool:
        return self._to_set().issuperset(other)

    def symmetric_difference(self, other: set):
        return self._to_set().symmetric_difference(other)

    def union(self, other: set):
        return self._to_set().union(other)

    def update(self, *others) -> None:
        self._to_set().update(others)

    def _to_set(self) -> set:
        result = set()
        for item in self:
            result.add(item)
        return result
