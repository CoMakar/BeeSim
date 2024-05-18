import math
import random as rng
from abc import ABC, abstractmethod

from src.bee import state, DeathReason, BeeEvent
from src.egg.member import GenericBeeEgg
from src.common import SimHiveObject, HasBehavior, HasUUID, SimObjectState
from lib.state_lib.transition_table import StateTransitionTable
from src.utils.num import clamp, linear_remap, deviate


class AbstractBee(ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()
        self.__weight = 0.0
        self.__age = 0
        
    @property
    def weight(self) -> float:
        return self.__weight
    
    @weight.setter
    def weight(self, value):
        self.__weight = max(0.0, value)
        
    @property
    def age(self) -> int:
        return self.__age
    
    @age.setter
    def age(self, value):
        self.__age = max(0, value)


class LiveBee(AbstractBee, SimHiveObject, HasBehavior, HasUUID):
    _starvation_cap = 1.0
    _starvation_inc_rate = 0.002
    _starvation_dec_rate = 0.001
    state: SimObjectState

    def __init__(self):
        super().__init__()
        self.__lifespan = 0
        self.__starvation_factor = 0.0
        
        self.__honey_consumption_multiplier = 0.0
        self.__rest_time = 0
    
    @property
    def lifespan(self) -> int:
        return self.__lifespan
    
    @lifespan.setter
    def lifespan(self, value):
        self.__lifespan = max(0, value)
        
    @property
    def starvation_rate(self) -> float:
        return self.__starvation_factor
    
    @starvation_rate.setter
    def starvation_rate(self, value):
        self.__starvation_factor = clamp(value, 0.0, self._starvation_cap)
        
    @property
    def honey_consumption_multiplier(self) -> float:
        return self.__honey_consumption_multiplier
    
    @honey_consumption_multiplier.setter
    def honey_consumption_multiplier(self, value):
        self.__honey_consumption_multiplier = clamp(value, 0.0, 1.0)
        
    @property
    def rest_time(self) -> int:
        return self.__rest_time
    
    @rest_time.setter
    def rest_time(self, value):
        self.__rest_time = max(0, value)
        
    @property
    def honey_consumption(self) -> float:
        return self.weight * self.honey_consumption_multiplier
            
    def consume_honey(self):
        honey_desired = self.honey_consumption
        honey_got = self.hive.take_honey(honey_desired)
        self.weight += honey_got / 100

        return honey_got >= honey_desired

    def die(self, reason: DeathReason):
        self.hive.bee_died(self, reason)
        
    def update(self):
        if self.lifespan == 0:
            self.die(DeathReason.NATURAL)
            return
        
        if self.starvation_rate == self._starvation_cap:
            self.die(DeathReason.STARVATION)
            return
    
        self.state.update()

        self.lifespan -= 1
        self.age += 1
        self.starvation_rate += self._starvation_inc_rate if not self.consume_honey() else -self._starvation_dec_rate


class DeadBee(AbstractBee, SimHiveObject, HasUUID):
    def __init__(self):
        super().__init__()
        self.__reason = DeathReason.UNKNOWN
        self.__was = LiveBee
        
    @property
    def reason(self):
        return self.__reason

    @reason.setter
    def reason(self, value):
        if not isinstance(value, DeathReason):
            raise ValueError("Invalid death reason type")
        
        self.__reason = value

    @property
    def was(self):
        return self.__was
    
    @was.setter
    def was(self, value):
        if not issubclass(value, LiveBee):
            raise ValueError("Invalid bee type")
        
        self.__was = value
        
        
class QueenBee(LiveBee):
    _behavior = StateTransitionTable({
        BeeEvent.RESTED: (state.Resting, state.LayingEggs),
        BeeEvent.LAID_EGG: (state.LayingEggs, state.Resting)
    })
    
    def __init__(self):
        super().__init__()
        self.lifespan = math.inf
        self.honey_consumption_multiplier = 0.0
        self.weight = 800

        self.fertility_base = 5
        self.fertility_max = 50
        self.rest_time = 1500
        
        self.bsm.set_state(state.Resting(self))

    @property
    def fertility(self):
        return max(1,
                   self.fertility_base - len(self.hive.dead_bees_in_hive) + round(linear_remap(self.hive.honey_amount,
                                                                                               0,
                                                                                               self.hive._honey_amount_cap,
                                                                                               0,
                                                                                               self.fertility_max))
                   )

    def lay_eggs(self):
        self.hive.add_eggs(GenericBeeEgg, self.fertility)


class DroneBee(LiveBee):
    _behavior = StateTransitionTable({
        BeeEvent.RESTED: (state.Resting, state.FertilizingEggs),
        BeeEvent.FERTILIZED_EGG: (state.FertilizingEggs, state.Resting)
    })
    
    def __init__(self):
        super().__init__()
        self.lifespan = round(deviate(1700, 0.2))
        self.honey_consumption_multiplier = deviate(0.15, 0.33)
        self.weight = 8
        
        self.fertility = round(deviate(1, 0.55))
        self.rest_time = round(deviate(400, 0.5))
        
        self.bsm.set_state(state.Resting(self))

    def fertilize_eggs(self):
        unfertilized = tuple(filter(lambda e: not e.is_fertilized, self.hive.eggs))

        amount = min(self.fertility, len(unfertilized))

        if amount == 0:
            return

        chosen = rng.sample(unfertilized, k=amount)

        for egg in chosen:
            self.hive.egg_fertilized(egg)


class WorkerBee(LiveBee):
    _behavior = StateTransitionTable({
        BeeEvent.RESTED: (state.Resting, state.HarvestingHoney),
        BeeEvent.FINISHED_WORK: ((state.HarvestingHoney, state.CleaningHive), (state.CleaningHive, state.Resting))
    })
    
    def __init__(self,):
        super().__init__()
        self.lifespan = round(deviate(4000, 0.15))
        self.honey_consumption_multiplier = deviate(0.1, 0.25)
        self.weight = 20
        
        self.honey_harvest_time = round(deviate(300, 0.07))
        self.honey_income_multiplier = 0.2
        self.honey_income_base = 20

        self.clean_attempts = 3

        self.rest_time = round(deviate(400, 0.2))

        self.bsm.set_state(state.Resting(self))

    @property
    def is_harvesting(self):
        return type(self.state) is state.HarvestingHoney
        
    @property
    def honey_income(self):
        return self.honey_income_base + self.weight * self.honey_income_multiplier
        
    def donate_honey(self):
        self.hive.put_honey(self.honey_income)
        
    def clean_hive(self):
        if len(self.hive.dead_bees_in_hive) == 0:
            return
        
        dead_bee = rng.choice(tuple(self.hive.dead_bees_in_hive))
        
        if self.weight >= dead_bee.weight:
            self.hive.dead_bee_cleaned(dead_bee)
        

class Larva(LiveBee):
    _behavior = StateTransitionTable({
        BeeEvent.GREW: (state.Growing, state.Transforming),
    })
    
    def __init__(self):
        super().__init__()
        self.lifespan = math.inf
        self.honey_consumption_multiplier = 0.3
        self.weight = 2
        
        self.growth_time = round(deviate(800, 0.2))
        
        self.bsm.set_state(state.Growing(self))
        
    def transform(self):
        self.hive.larva_transformed(self)
