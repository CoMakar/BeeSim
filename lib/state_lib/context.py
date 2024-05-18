from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union, Any

from . import state as _st_
from .helper import AbstractSingleton


class Context(ABC):
    @abstractmethod
    def __init__(self, state: _st_.State = None):
        self.__state = None
        self.state = state

    @property
    def state(self) -> Union[_st_.State, None]:
        return self.__state
    
    @state.setter
    def state(self, value: Union[_st_.State, None]):
        if value is not None and not isinstance(value, _st_.State):
            raise TypeError(f"State must be an instance of `State` or None: {type(value) = }")

        self.__state = value

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"


class NullContext(Context, metaclass=AbstractSingleton):
    def __init__(self, *args, **kwargs):
        Context.__init__(self, None)
        
    @property
    def state(self):
        return None
        
    @state.setter
    def state(self, value: Any):
        pass
