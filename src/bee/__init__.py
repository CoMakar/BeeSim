from enum import Enum

from lib.state_lib import EventEnum


class BeeEvent(EventEnum):
    RESTED = "rested"
    LAID_EGG = "laid_egg"
    FERTILIZED_EGG = "fertilized_egg"
    GREW = "grew"
    TRANSFORMED = "transformed"
    FINISHED_WORK = "finished_work"


class DeathReason(Enum):
    UNKNOWN = "unknown"
    NATURAL = "natural"
    STARVATION = "starvation"
    OVERCROWDED = "overcrowded"
