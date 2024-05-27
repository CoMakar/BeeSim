import itertools as ittls
import random as rng
from typing import Iterable, Collection

from src.utils import Number


def linspace(start: Number, stop: Number, num: int, endpoint: bool = True):
    """
    Recreation of linspace function from numpy

    Returns:
        - linearly distributed values from `start` to `stop` with `num` samples
        - if `endpoint` is True `stop` will be included
    """

    if type(num) is not int:
        raise TypeError("Required: num: int")

    if num <= 1:
        raise ValueError("Required: num > 1")

    step = (stop - start) / (num - 1) if endpoint else (stop - start) / num

    return tuple(start + step * n for n in range(num))


def linear_remap(value: Number,
                 from_min: Number, from_max: Number,
                 to_min: Number, to_max: Number):

    if from_min >= from_max:
        raise ValueError("Required: from_min < from_max")
    if to_min >= to_max:
        raise ValueError("Required: to_min < to_max")

    scale = (value - from_min) / (from_max - from_min)
    return to_min + scale * (to_max - to_min)


def clamp(number: Number, min_val: Number, max_val: Number):
    if max_val < min_val:
        raise ValueError("Required: max_val >= min_val required")

    return max(min(number, max_val), min_val)


def pairwise(iterable: Iterable):
    """
    Returns:
        - tuple of initial values related in pairs
    """

    if not isinstance(iterable, Iterable):
        raise TypeError("Required: iterable: Iterable")

    iterable_0, iterable_1 = ittls.tee(iterable)
    next(iterable_1)
    return zip(iterable_0, iterable_1)


def deviate(value: Number, factor: float) -> float:
    base = value * factor
    deviation = rng.uniform(-base, base)
    return value + deviation


def avg(collection: Collection[Number]):
    return sum(collection) / len(collection)
