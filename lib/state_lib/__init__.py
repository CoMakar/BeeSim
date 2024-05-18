from enum import Enum


class EventEnum(Enum):
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self})"
