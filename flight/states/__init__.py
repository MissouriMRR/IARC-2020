"""Used to export the states"""
from flight.states.state import State
from flight.states.start import Start
from flight.states.takeoff import Takeoff
from flight.states.land import Land
from flight.states.final import Final
from flight.states.early_laps import EarlyLaps
from flight.states.to_mast import ToMast
from flight.states.detect_module import DetectModule
from flight.states.simple_takeoff import SimpleTakeoff

STATES = {
    "start": Start,
    "takeoff": Takeoff,
    "early_laps": EarlyLaps,
    "land": Land,
    "final": Final,
    "to_mast": ToMast,
    "detect_module": DetectModule,
    "simple_takeoff": SimpleTakeoff
}
