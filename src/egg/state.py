from __future__ import annotations
from typing import TYPE_CHECKING

from src.egg import EggEvent
from src.common import SimObjectState
from lib.state_lib.state import TempState, FinalState

if TYPE_CHECKING:
    from src.egg.member import BeeEgg


class EggState(SimObjectState):
    context: BeeEgg

    def __init__(self, egg: BeeEgg):
        super().__init__(egg)

    @property
    def egg(self) -> BeeEgg:
        return self.context


class Growing(EggState, TempState):
    def __init__(self, egg: BeeEgg):
        super().__init__(egg)
        self.time_left = egg.hatching_time
    
    def once_zero_reached(self):
        self.egg.bsm.next_state(EggEvent.GREW, self.egg)
    
    def update(self):
        self.tick_down()
    
        
class Hatching(EggState, FinalState):
    def after_enter(self):
        self.egg.hatch()
