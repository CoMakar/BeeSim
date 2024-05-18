from typing import Union
import pyxel

from src.utils import Number
from src.utils.vec import Vec2


class Icon:
    def __init__(self, width: Number, height: Number,
                 u: Number, v: Number,
                 bank: Union[int, pyxel.Image], transparency_key: Union[int, None] = None):

        self.__size = Vec2(width, height)
        self.__uv = Vec2(u, v)

        self.__bank = bank
        self.__transparency_key = transparency_key

    def draw(self, x: Number, y: Number):
        pyxel.blt(x, y, self.__bank,
                  *self.__uv.as_tuple, *self.__size.as_tuple,
                  self.__transparency_key)
