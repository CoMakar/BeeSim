from __future__ import annotations
from abc import ABC, abstractmethod

from . import context as _ctx_
from .helper import AbstractSingleton


class State(ABC):
    @abstractmethod
    def __init__(self, context: _ctx_.Context = _ctx_.NullContext()):
        self.__context = ...
        self.context = context
        
    def before_exit(self):
        pass

    def after_exit(self):
        pass
    
    def before_enter(self):
        pass
    
    def after_enter(self):
        pass
    
    @property
    def context(self) -> _ctx_.Context:
        return self.__context

    @context.setter
    def context(self, value):
        if not isinstance(value, _ctx_.Context):
            raise TypeError(f"Context must be an instance of `Context`: {type(value) = }")

        self.__context = value
    
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"


class NullState(State, metaclass=AbstractSingleton):
    def __init__(self, *args, **kwargs):
        State.__init__(self, _ctx_.NullContext())
    

class InitialState(State, ABC):
    ...


class FinalState(State, ABC):
    ...
    

class TempState(State, ABC):
    @abstractmethod
    def __init__(self, context: _ctx_.Context, time_left: int = 1):
        State.__init__(self, context)
        
        if type(time_left) is not int:
            raise TypeError(f"Time left must be an integer: {type(time_left) = }")
        
        if time_left <= 0:
            raise ValueError(f"Initial time must different from 0: {time_left = }")
        
        self.__time_left: int = 1
        self.time_left = time_left

    def tick_down(self):
        self.time_left -= 1
        
    def tick_up(self):
        self.time_left += 1
        
    def add_time(self, time: int):
        self.time_left += time
        
    def sub_time(self, time: int):
        self.time_left -= time
        
    def once_zero_reached(self):
        pass
        
    @property
    def time_is_up(self) -> bool:
        return self.time_left <= 0
    
    @property
    def time_left(self) -> int:
        return self.__time_left
    
    @time_left.setter
    def time_left(self, value: int):
        if self.time_is_up:
            return
        
        if value <= 0:
            self.__time_left = 0
            self.once_zero_reached()
        
        else:
            self.__time_left = value
