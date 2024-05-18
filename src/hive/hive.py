from __future__ import annotations
from typing import Set, TYPE_CHECKING, Type
from collections import Counter

import src.bee.member as _bees_
import src.egg.member as _eggs_
from src.bee import DeathReason
from src.egg import EggEvent
from src.common import SimObject
from src.hive.factory import HiveElementFactory
from src.utils.num import clamp

if TYPE_CHECKING:
    from src.bee.member import DeadBee, Larva, LiveBee
    from src.egg.member import BeeEgg


class Hive(SimObject):
    _honey_take_cap = 100.0
    _honey_amount_cap = 500000.0
    _eggs_cap = 100

    def __init__(self, drones_amount: int, workers_amount: int,
                 eggs_amount: int, honey_amount: float):        
        self.honey_amount = honey_amount
        self.__factory = HiveElementFactory(self)

        self.__eggs: Set[BeeEgg] = set()
        self.__live_bees: Set[LiveBee] = set()
        self.__dead_bees_in_hive: Set[DeadBee] = set()
        self.__dead_bees_in_grave: Set[DeadBee] = set()

        self.__queen_bee = self.__factory.create_bee(_bees_.QueenBee)
        self.add_bees(_bees_.DroneBee, drones_amount)
        self.add_bees(_bees_.WorkerBee, workers_amount)
        self.add_eggs(_eggs_.GenericBeeEgg, eggs_amount)

        ...

    @property
    def queen_bee(self):
        return self.__queen_bee
    
    @property
    def eggs(self):
        return self.__eggs    
    
    @property
    def live_bees(self):
        return self.__live_bees
    
    @property
    def dead_bees_in_hive(self):
        return self.__dead_bees_in_hive
    
    @property
    def dead_bees_in_grave(self):
        return self.__dead_bees_in_grave

    @property
    def all_dead_bees(self):
        return self.dead_bees_in_grave.union(self.dead_bees_in_hive)

    @property
    def honey_amount(self):
        return self.__honey_amount

    @honey_amount.setter
    def honey_amount(self, value):
        self.__honey_amount = clamp(value, 0.0, self._honey_amount_cap)

    def take_honey(self, amount: float):
        amount = min(
            amount,
            self._honey_take_cap,
            self.honey_amount,
        )

        self.honey_amount -= amount

        return amount

    def put_honey(self, amount: float):
        self.honey_amount += amount

    def add_eggs(self, egg_type: Type[_eggs_.BeeEgg], amount: int):
        amount = min(amount, self._eggs_cap - len(self.eggs))
        self.eggs.update(self.__factory.create_egg(egg_type) for _ in range(amount))

    def add_bees(self, bee_type: Type[_bees_.LiveBee], amount: int):
        self.live_bees.update(self.__factory.create_bee(bee_type) for _ in range(amount))

    def egg_fertilized(self, egg: BeeEgg):
        egg.bsm.next_state(EggEvent.WAS_FERTILIZED, egg)

    def egg_hatched(self, egg: BeeEgg):
        self.eggs.remove(egg)
        self.add_bees(_bees_.Larva, 1)

    def larva_transformed(self, larva: Larva):
        self.live_bees.remove(larva)
        self.live_bees.add(self.__factory.create_bee_from_larva(larva))

    def bee_died(self, bee: LiveBee, reason: DeathReason):
        self.live_bees.remove(bee)
        self.dead_bees_in_hive.add(self.__factory.create_dead_bee(bee, reason))

    def dead_bee_cleaned(self, dead_bee: DeadBee):
        self.dead_bees_in_hive.remove(dead_bee)
        self.dead_bees_in_grave.add(dead_bee)
        
    def update(self):
        self.queen_bee.update()

        for bee in self.__live_bees.copy():
            bee.update()

        for egg in self.__eggs.copy():
            egg.update()

    @property
    def live_bees_type_count(self):
        return Counter((type(bee) for bee in self.__live_bees))

    @property
    def all_dead_bees_was_count(self):
        return Counter(bee.was for bee in self.all_dead_bees)

    @property
    def all_dead_bees_reason_count(self):
        return Counter(bee.reason for bee in self.all_dead_bees)

    @property
    def dead_bees_in_hive_was_count(self):
        return Counter((bee.was for bee in self.dead_bees_in_hive))

    @property
    def eggs_status_count(self):
        return Counter(egg.is_fertilized for egg in self.eggs)

    @property
    def honey_consumption(self):
        return sum(b.honey_consumption for b in self.live_bees)

    @property
    def honey_income(self):
        return sum(b.honey_income for b in filter(lambda b: isinstance(b, _bees_.WorkerBee) and b.is_harvesting, self.live_bees))

    @property
    def drone_efficiency_factor(self):
        if len(self.eggs) == 0:
            return 1

        return sum(1 for egg in self.eggs if egg.is_fertilized) / len(self.eggs)
