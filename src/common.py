from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from lib.state_lib.state import State
from lib.state_lib.context import Context, NullContext
from lib.state_lib.transition_table import StateTransitionTable
from lib.state_lib.fsm import FiniteStateMachine

if TYPE_CHECKING:
    from src.hive.hive import Hive


class SimObjectState(State, ABC):
    def update(self):
        pass


class Idle(SimObjectState):
    def __init__(self, *args, **kwargs):
        super().__init__(NullContext())


class BehavioralStateMachine(FiniteStateMachine):
    state: SimObjectState

    def __init__(self, transition_table: StateTransitionTable, context: Context, initial_state: State = Idle()):
        super().__init__(transition_table, initial_state, context)


class SimObject(ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()

    def update(self):
        pass


class HiveElement(ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()
        self.__hive: Hive = ...
        
    @property
    def hive(self) -> Hive:
        return self.__hive

    def set_hive(self, hive: Hive):
        self.__hive = hive


class SimHiveObject(SimObject, HiveElement):
    @abstractmethod
    def __init__(self):
        super().__init__()
        

class HasBehavior(Context):
    state: SimObjectState
    _behavior = StateTransitionTable()

    @abstractmethod
    def __init__(self):
        super().__init__()
        self.__bsm = BehavioralStateMachine(self._behavior, self)
    
    @property
    def bsm(self):
        return self.__bsm


class HasUUID(ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()
        self.__id = uuid.uuid4()

    @property
    def uuid(self):
        return self.__id
