from abc import ABC, abstractmethod

from src.egg import state, EggEvent
from src.common import Idle, SimHiveObject, HasBehavior, HasUUID, SimObjectState
from lib.state_lib.transition_table import StateTransitionTable


class AbstractEgg(ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()
        self.__hatching_time = 0
        
    @property
    def hatching_time(self) -> int:
        return self.__hatching_time
    
    @hatching_time.setter
    def hatching_time(self, value):
        self.__hatching_time = max(0, value)
    
    @abstractmethod 
    def hatch(self):
        pass


class BeeEgg(AbstractEgg, SimHiveObject, HasBehavior, HasUUID):
    state: SimObjectState

    def __init__(self):
        super().__init__()

    def update(self):
        self.state.update()
        
    def hatch(self):
        self.hive.egg_hatched(self)

    @property
    def is_fertilized(self):
        return type(self.state) is state.Growing


class GenericBeeEgg(BeeEgg):
    _behavior = StateTransitionTable({
        EggEvent.WAS_FERTILIZED: (Idle, state.Growing),
        EggEvent.GREW: (state.Growing, state.Hatching)
    })
    
    def __init__(self):
        super().__init__()
        self.hatching_time = 1000
        
        self.bsm.set_state(Idle())
