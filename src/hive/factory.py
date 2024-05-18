from __future__ import annotations
import random as rng
from typing import Type, TYPE_CHECKING

from src.bee import DeathReason
from src.bee.member import LiveBee, DroneBee, WorkerBee, Larva, DeadBee
from src.egg.member import BeeEgg


if TYPE_CHECKING:
    from src.hive.hive import Hive


class HiveElementFactory:
    def __init__(self, hive: Hive):
        self.hive = hive

    def create_bee(self, bee_type: Type[LiveBee]) -> LiveBee:
        if not issubclass(bee_type, LiveBee):
            raise ValueError("Unknown bee type")

        bee = bee_type()
        bee.set_hive(self.hive)

        return bee

    def create_bee_from_larva(self, larva: Larva) -> LiveBee:
        possible_bee_types = (DroneBee, WorkerBee)

        bee_type = rng.choice(possible_bee_types)
        bee = self.create_bee(bee_type)

        bee.weight = bee.weight + larva.weight / 10
        bee.age = larva.age

        return bee

    def create_dead_bee(self, was: LiveBee, reason: DeathReason) -> DeadBee:
        if not issubclass(type(was), LiveBee):
            raise ValueError("Unknown bee type")

        bee = DeadBee()

        bee.set_hive(was.hive)
        bee.weight = was.weight / 2
        bee.age = was.age
        bee.reason = reason
        bee.was = type(was)

        return bee

    def create_egg(self, egg_type: Type[BeeEgg]) -> BeeEgg:
        if not issubclass(egg_type, BeeEgg):
            raise ValueError("Unknown egg type")

        egg = egg_type()
        egg.set_hive(self.hive)

        return egg
