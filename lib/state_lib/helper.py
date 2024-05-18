from abc import ABCMeta as AbstractMeta
from typing import Any, Dict, Type


def is_of_class_type(obj: Any, cls: Type):
    return (isinstance(obj, type)
            and not isinstance(obj, cls)
            and issubclass(obj, cls))


class AbstractSingleton(AbstractMeta):
    __instances: Dict[Type, Type] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(AbstractSingleton, cls).__call__(*args, **kwargs)
            
        return cls.__instances[cls]
