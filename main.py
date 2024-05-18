from collections import Counter, deque
from dataclasses import dataclass
import pyxel

import src.bee.member as bees
from src.bee import DeathReason
from src.hive.hive import Hive
from src.utils.num import avg
from src.widgets.icon import Icon
from src.widgets.graph import Graph


@dataclass(frozen=True)
class Icons:
    pause = Icon(8, 8, 8, 0, 0)
    play = Icon(8, 8, 16, 0, 0)
    honey = Icon(8, 8, 24, 0, 0)
    bee = Icon(8, 8, 24, 8, 0)
    egg = Icon(8, 8, 24, 16, 0)
    crown = Icon(8, 8, 0, 8, 0)
    w = Icon(8, 8, 8, 8, 0)
    d = Icon(8, 8, 0, 16, 0)
    l = Icon(8, 8, 8, 16, 0)
    bad = Icon(8, 8, 0, 24, 0)
    ok = Icon(8, 8, 8, 24, 0)
    stats = Icon(8, 8, 16, 8, 0)
    arrows = Icon(8, 8, 16, 16, 0)
    arrow_down = Icon(8, 8, 0, 32, 0)
    arrow_up = Icon(8, 8, 8, 32, 0)
    grave = Icon(8, 8, 16, 24, 0)
    trash = Icon(8, 8, 24, 24, 0)
    tilda = Icon(8, 8, 16, 32, 0)


@dataclass
class Data:
    live_bees_type_count = Counter()
    dead_bees_in_hive_count = Counter()
    all_dead_bees_was_count = Counter()
    all_dead_bees_reason_count = Counter()
    eggs_status_count = Counter()
    honey_amount = 0.0
    honey_income = deque(maxlen=4)
    honey_consumption = deque(maxlen=4)
    drones_efficiency = deque(maxlen=2)
    queen_fertility = 0


class App:
    _WIDTH = 320
    _HEIGHT = 320
    _GRAPH_STEEPNESS = 1
    _HIVE_DATA_TRANSFER_EVERY_NTH_FRAME = 5
    _FPS = 120

    _INITIAL_DRONES = 3
    _INITIAL_WORKERS = 10
    _INITIAL_EGGS = 10
    _INITIAL_HONEY = 50000.0

    icons: Icons = Icons()
    data: Data = Data()

    def __init__(self):
        pyxel.init(self._WIDTH, self._HEIGHT, quit_key=None, title="Bees", display_scale=2, fps=self._FPS)
        pyxel.load("./res.pyxres")

        self.active = True

        self.hive = Hive(self._INITIAL_DRONES, self._INITIAL_WORKERS, self._INITIAL_EGGS, self._INITIAL_HONEY)

        self.honey_graph = Graph(2, 2,
                                 self._WIDTH - 4, 100,
                                 0, self.hive._honey_amount_cap,
                                 self._GRAPH_STEEPNESS, graph_color=10)

        pyxel.run(self.update, self.draw)

    ...

    def update(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.active = not self.active

        if self.active:
            self.hive.update()

        if pyxel.frame_count % self._HIVE_DATA_TRANSFER_EVERY_NTH_FRAME == 0 and self.active:
            self.data.live_bees_type_count = self.hive.live_bees_type_count
            self.data.dead_bees_in_hive_count = self.hive.dead_bees_in_hive_was_count
            self.data.all_dead_bees_reason_count = self.hive.all_dead_bees_reason_count
            self.data.all_dead_bees_was_count = self.hive.all_dead_bees_was_count
            self.data.eggs_status_count = self.hive.eggs_status_count

            self.data.honey_amount = self.hive.honey_amount
            self.data.honey_income.append(self.hive.honey_income)
            self.data.honey_consumption.append(self.hive.honey_consumption)
            self.data.drones_efficiency.append(self.hive.drone_efficiency_factor)

            self.data.queen_fertility = self.hive.queen_bee.fertility

            self.honey_graph.add_value(self.hive.honey_amount)

    def draw(self):
        pyxel.cls(0)
        self.honey_graph.draw()
        self.draw_graph_stats()
        self.draw_stats()
        self.draw_bees()
        self.draw_eggs()
        self.draw_dead()
        self.draw_extra()

    def draw_graph_stats(self):
        x, y = 4, 4

        status_icon = self.icons.arrow_up \
            if avg(self.data.honey_income) > avg(self.data.honey_consumption) \
            else self.icons.arrow_down

        avg_income = avg(self.data.honey_income)
        avg_consumption = avg(self.data.honey_consumption)
        honey_balance = avg_income - avg_consumption

        balance_color = 11 if honey_balance > 0 else 8

        status_icon.draw(x, y + 5)
        pyxel.text(x + 10, y + 2, f"+{avg_income:.2f}", 11)
        pyxel.text(x + 10, y + 12, f"-{avg_consumption:.2f}", 8)

        pyxel.text(x + 3, y + 22, "=", balance_color)
        pyxel.text(x + 10, y + 22, f"{honey_balance:+.2f}", balance_color)

    def draw_stats(self):
        x, y = self._WIDTH // 2 - 30, 104

        self.icons.stats.draw(x, y)
        pyxel.text(x + 10, y + 2, f"Stats:", 7)

        self.icons.honey.draw(x, y + 10)
        pyxel.text(x + 10, y + 12, f"{self.data.honey_amount:.2f}", 10)

        efc = avg(self.data.drones_efficiency)
        efc_icon = self.icons.ok if efc >= 0.5 else self.icons.bad
        efc_color = 11 if efc >= 0.5 else 8

        efc_icon.draw(x, y + 20)
        pyxel.text(x + 10, y + 22, f"Drones efficiency: {avg(self.data.drones_efficiency) * 100:.0f}%", efc_color)

        self.icons.crown.draw(x, y + 30)
        pyxel.text(x + 10, y + 32, f"Fertility:", 10)
        pyxel.text(x + 60, y + 32, f"{self.data.queen_fertility}", 10)

    def draw_bees(self):
        x, y = 20, 180

        self.icons.bee.draw(x, y)
        pyxel.text(x + 10, y + 2, f"Live bees:", 7)
        pyxel.text(x + 60, y + 2, f"{self.data.live_bees_type_count.total()}", 7)

        self.icons.w.draw(x, y + 20)
        pyxel.text(x + 10, y + 22, f"Worker bees:", 7)
        pyxel.text(x + 60, y + 22, f"{self.data.live_bees_type_count.get(bees.WorkerBee, 0)}", 7)

        self.icons.d.draw(x, y + 30)
        pyxel.text(x + 10, y + 32, f"Drone bees:", 7)
        pyxel.text(x + 60, y + 32, f"{self.data.live_bees_type_count.get(bees.DroneBee, 0)}", 7)

        self.icons.l.draw(x, y + 40)
        pyxel.text(x + 10, y + 42, f"Larva:", 7)
        pyxel.text(x + 60, y + 42, f"{self.data.live_bees_type_count.get(bees.Larva, 0)}", 7)

        self.icons.crown.draw(x, y + 50)
        pyxel.text(x + 10, y + 52, f"Queen", 10)
        pyxel.text(x + 60, y + 52, f"1", 10)

    def draw_eggs(self):
        x, y = 110, 180

        self.icons.egg.draw(x, y)
        pyxel.text(x + 10, y + 2, f"Eggs", 7)
        pyxel.text(x + 70, y + 2, f"{self.data.eggs_status_count.total()}", 7)

        pyxel.text(x + 10, y + 22, f"Unfertilized:", 7)
        pyxel.text(x + 70, y + 22, f"{self.data.eggs_status_count.get(0, 0)}", 7)

        pyxel.text(x + 10, y + 32, f"Fertilized:", 7)
        pyxel.text(x + 70, y + 32, f"{self.data.eggs_status_count.get(1, 0)}", 7)

    def draw_dead(self):
        x, y = 230, 180

        total_dead = self.data.all_dead_bees_reason_count.total()
        natural = self.data.all_dead_bees_reason_count.get(DeathReason.NATURAL, 0)
        starvation = self.data.all_dead_bees_reason_count.get(DeathReason.STARVATION, 0)

        self.icons.grave.draw(x, y)
        pyxel.text(x + 10, y + 2, f"Dead bees:", 7)
        pyxel.text(x + 60, y + 2, f"{total_dead}", 7)

        self.icons.w.draw(x, y + 20)
        pyxel.text(x + 10, y + 22, f"Worker bees:", 7)
        pyxel.text(x + 60, y + 22, f"{self.data.all_dead_bees_was_count.get(bees.WorkerBee, 0)}", 7)

        self.icons.d.draw(x, y + 30)
        pyxel.text(x + 10, y + 32, f"Drone bees:", 7)
        pyxel.text(x + 60, y + 32, f"{self.data.all_dead_bees_was_count.get(bees.DroneBee, 0)}", 7)

        self.icons.l.draw(x, y + 40)
        pyxel.text(x + 10, y + 42, f"Larva:", 7)
        pyxel.text(x + 60, y + 42, f"{self.data.all_dead_bees_was_count.get(bees.Larva, 0)}", 7)

        self.icons.trash.draw(x, y + 60)
        pyxel.text(x + 10, y + 62, f"Uncleaned:", 7)
        pyxel.text(x + 60, y + 62, f"{self.data.dead_bees_in_hive_count.total()}", 7)

        percent = natural / total_dead if total_dead != 0 else 0
        pyxel.text(x + 10, y + 82, f"Natural:", 7)
        pyxel.text(x + 60, y + 82, f"{natural}", 7)
        pyxel.text(x + 40, y + 92, f"(%)", 13)
        pyxel.text(x + 60, y + 92, f"{percent * 100:.0f}%", 13)

        percent = starvation / total_dead if total_dead != 0 else 0
        pyxel.text(x + 10, y + 102, f"Starvation:", 7)
        pyxel.text(x + 60, y + 102, f"{starvation}", 7)
        pyxel.text(x + 40, y + 112, f"(%)", 13)
        pyxel.text(x + 60, y + 112, f"{percent * 100 :.0f}%", 13)

    def draw_extra(self):
        if self.active:
            self.icons.play.draw(self._WIDTH - 12, self._HEIGHT - 12)
            pyxel.text(self._WIDTH - 115, self._HEIGHT - 10, "Press <space> to pause...", 13)
        else:
            self.icons.pause.draw(self._WIDTH - 12, self._HEIGHT - 12)
            pyxel.text(self._WIDTH - 40, self._HEIGHT - 10, "Paused", 13)

        pyxel.text(2, self._HEIGHT - 10, f"(v.1.0)", 13)


def main():
    App()


if __name__ == '__main__':
    main()
