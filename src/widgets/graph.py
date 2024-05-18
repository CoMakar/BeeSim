from collections import deque
import pyxel

from src.utils import Number
from src.utils.vec import Vec2, Vec3
from src.utils.num import linspace, linear_remap, clamp, pairwise


class Graph:
    def __init__(self, pos_x: Number, pos_y: Number,
                 width: Number, height: Number,
                 min_y: Number, max_y: Number,
                 step: int = 1,
                 graph_color: int = 3, border_color: int = 7, grid_color: int = 1):

        if step < 1:
            raise ValueError(f"Required: step >= 1; Got: {step = }")

        if min_y >= max_y:
            raise ValueError(f"Required: min_y < max_y; Got: {min_y = }, {max_y = }")

        self.__pos = Vec2(pos_x, pos_y)
        self.__size = Vec2(max(2, width), max(2, height))

        self.__y_domain = Vec2(min_y, max_y)
        self.__step = step

        self.__graph_data = deque(maxlen=self.size.x)
        self.__real_data = deque(maxlen=self.size.x)

        self.__color = Vec3(graph_color, border_color, grid_color)

    @property
    def pos(self):
        return self.__pos

    def move(self, delta: Vec2):
        self.__pos += delta

    def set_pos(self, pos: Vec2):
        self.__pos = pos

    @property
    def size(self):
        return self.__size

    def resize_width(self, width: Number):
        self.__size = Vec2(max(2, width), self.size.y)
        self.__real_data = deque(self.__real_data, maxlen=self.size.x)
        self.__graph_data = deque(self.__graph_data, maxlen=self.size.x)

    def resize_height(self, height: Number):
        self.__size = Vec2(self.size.x, max(2, height))
        self.__recalc_graph()

    @property
    def y_domain(self):
        return self.__y_domain

    def set_y_domain(self, min_y: Number, max_y: Number):
        if min_y >= max_y:
            raise ValueError(f"Required: min_y < max_y; Got: {min_y = }, {max_y = }")

        self.__y_domain = Vec2(min_y, max_y)
        self.__recalc_graph()

    @property
    def step(self):
        return self.__step

    def set_step(self, step: int):
        if not isinstance(step, int) or step < 1:
            raise ValueError("Step must be a positive integer")

        self.__step = step

    def draw(self):
        pyxel.rectb(self.pos.x - 1, self.pos.y - 1,
                    self.size.x + 2, self.size.y + 2,
                    self.__color.y)

        if self.size.x >= 5 and self.size.y >= 5:
            pyxel.line(pyxel.floor(self.pos.x + self.size.x / 2), self.pos.y,
                       pyxel.floor(self.pos.x + self.size.x / 2), self.pos.y + self.size.y - 1,
                       self.__color.z)
            pyxel.line(self.pos.x, pyxel.floor(self.pos.y + self.size.y / 2),
                       self.pos.x + self.size.x - 1, pyxel.floor(self.pos.y + self.size.y / 2),
                       self.__color.z)

        if len(self.__graph_data) == 0:
            return

        for p1, p2 in pairwise(enumerate(self.__graph_data)):
            pyxel.line(self.pos.x + p1[0], self.pos.y - p1[1] + self.size.y,
                       self.pos.x + p2[0], self.pos.y - p2[1] + self.size.y,
                       self.__color.x)

    def add_value(self, value: Number):
        if any((
                len(self.__real_data) == 0,
                self.__step == 1
        )):
            self.__real_data.append(value)
        else:
            self.__real_data.extend(linspace(self.__real_data[-1], value, self.__step))

        self.__recalc_graph()

    def clear(self):
        self.__real_data.clear()
        self.__graph_data.clear()

    def __remap(self, value: Number):
        return linear_remap(
            clamp(value, self.y_domain.x, self.y_domain.y),
            self.y_domain.x, self.y_domain.y, 1, self.size.y
        )

    def __recalc_graph(self):
        self.__graph_data = deque(
            [self.__remap(v) for v in self.__real_data],
            maxlen=self.size.x
        )
