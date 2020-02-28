from .Start import Start
from .Takeoff import Takeoff
from .State import State

STATES = {"start": Start, "takeoff": Takeoff, "land": None, "final": None}
