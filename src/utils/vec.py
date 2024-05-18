import math
from dataclasses import dataclass
from typing import Any

from src.utils import Number


@dataclass(frozen=True)
class Vec2:
    x: Number
    y: Number

    @property
    def as_tuple(self):
        return (self.x, self.y)

    def __validate(self, other):
        if not isinstance(other, Vec2):
            raise TypeError(f"Required: type(other) = Vec2; Got {type(other) = }")

    def __add__(self, other: 'Vec2'):
        self.__validate(other)
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vec2'):
        self.__validate(other)
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: Number):
        if not isinstance(scalar, Number):
            raise TypeError(f"Required: type(scalar) = float | int; Got: {type(scalar) = }")

        return Vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: Number):
        return self.__mul__(scalar)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __eq__(self, other: Any):
        if not isinstance(other, Vec2):
            return False

        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"{{{self.x}, {self.y}}}"

    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"

    @property
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    @property
    def normalized(self):
        return Vec2(0, 0) if self.length == 0 else Vec2(self.x / self.length, self.y / self.length)


@dataclass(frozen=True)
class Vec3:
    x: Number
    y: Number
    z: Number

    @property
    def as_tuple(self):
        return (self.x, self.y, self.z)

    def __validate(self, other):
        if not isinstance(other, Vec3):
            raise TypeError(f"Required: type(other) = Vec3; Got {type(other) = }")

    def __add__(self, other: 'Vec3'):
        self.__validate(other)
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vec3'):
        self.__validate(other)
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: Number):
        if not isinstance(scalar, Number):
            raise TypeError(f"Required: type(scalar) = float | int; Got: {type(scalar) = }")

        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: Number):
        return self.__mul__(scalar)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def __eq__(self, other: Any):
        if not isinstance(other, Vec3):
            return False

        return self.x == other.x and self.y == other.y and self.z == other.z

    def __str__(self):
        return f"{{{self.x}, {self.y}, {self.z}}}"

    def __repr__(self):
        return f"Vec2({self.x}, {self.y}, {self.z})"

    @property
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    @property
    def normalized(self):
        return Vec3(0, 0, 0) if self.length == 0 else Vec3(self.x / self.length,
                                                           self.y / self.length,
                                                           self.z / self.length)
