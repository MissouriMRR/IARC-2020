"""Used to export the states"""
from .state import State
from .start import Start
from .takeoff import Takeoff
from .land import Land
from .final import Final
from .early_laps import EarlyLaps

STATES = {
    "start": Start,
    "takeoff": Takeoff,
    "early_laps": EarlyLaps,
    "land": Land,
    "final": Final,
}
