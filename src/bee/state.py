from __future__ import annotations
from typing import TYPE_CHECKING

from src.bee import BeeEvent
from src.common import SimObjectState
from lib.state_lib.state import TempState, FinalState

if TYPE_CHECKING:
    from src.bee.member import LiveBee, QueenBee, DroneBee, WorkerBee, Larva


class BeeState(SimObjectState):
    context: LiveBee

    def __init__(self, bee: LiveBee):
        super().__init__(bee)

    @property
    def bee(self) -> LiveBee:
        return self.context


class Resting(BeeState, TempState):
    def __init__(self, bee: LiveBee):
        super().__init__(bee)
        self.time_left = bee.rest_time

    def once_zero_reached(self):
        self.bee.bsm.next_state(BeeEvent.RESTED, self.bee)

    def update(self):
        self.tick_down()


class LayingEggs(BeeState):
    bee: QueenBee

    def after_enter(self):
        self.bee.lay_eggs()
        self.bee.bsm.next_state(BeeEvent.LAID_EGG, self.bee)


class FertilizingEggs(BeeState):
    bee: DroneBee

    def after_enter(self):
        self.bee.fertilize_eggs()
        self.bee.bsm.next_state(BeeEvent.FERTILIZED_EGG, self.bee)


class HarvestingHoney(BeeState, TempState):
    bee: WorkerBee

    def __init__(self, bee: WorkerBee):
        super().__init__(bee)
        self.time_left = bee.honey_harvest_time

    def once_zero_reached(self):
        self.bee.bsm.next_state(BeeEvent.FINISHED_WORK, self.bee)

    def update(self):
        self.bee.donate_honey()
        self.tick_down()


class CleaningHive(BeeState, TempState):
    bee: WorkerBee

    def __init__(self, bee: WorkerBee):
        super().__init__(bee)
        self.time_left = bee.clean_attempts
        
    def once_zero_reached(self):
        self.bee.bsm.next_state(BeeEvent.FINISHED_WORK, self.bee)

    def update(self):
        self.bee.clean_hive()
        self.tick_down()


class Growing(BeeState, TempState):
    bee: Larva

    def __init__(self, bee: Larva):
        super().__init__(bee)
        self.time_left = bee.growth_time
    
    def once_zero_reached(self):
        self.bee.bsm.next_state(BeeEvent.GREW, self.bee)
    
    def update(self):            
        self.tick_down()


class Transforming(BeeState, FinalState):
    bee: Larva
        
    def after_enter(self):
        self.bee.transform()
