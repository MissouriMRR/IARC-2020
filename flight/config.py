"""Sets parameters for the drone and holds constant values needed for configuration"""
from flight.utils.latlon import LatLon, Latitude, Longitude

from mavsdk import System

NUM_LAPS: int = 2

# Typical Sparky flight test speed: 6.352 m/s
MAX_SPEED: float = 3  # m/s

ALT_CORRECTION_SPEED: float = 0.25  # m/s down
MAX_ALT: float = 8.0  # m
TAKEOFF_ALT: float = 1.0  # m
MAST_ALT: float = 1.3  # m
FLYING_ALT: float = 5.0  # m

# What percentage of the height can we lose/gain before unsafe
ALT_PERCENT_ACCURACY: float = 0.15
ALT_RANGE_MAX: float = FLYING_ALT + (FLYING_ALT * ALT_PERCENT_ACCURACY)  # m
ALT_RANGE_MIN: float = FLYING_ALT - (FLYING_ALT * ALT_PERCENT_ACCURACY)  # m

POINT_PERCENT_ACCURACY: float = 0.2

# Position for pylon 1
lat1: Latitude = Latitude(degree=37, minute=56, second=55.6)  # 37.948778
lon1: Longitude = Longitude(degree=-91, minute=-47, second=-3.3)  # -91.78425
pylon1: LatLon = LatLon(lat1, lon1)

# Position for pylon 2
lat2: Latitude = Latitude(degree=37, minute=56, second=53.3)  # 37.948139
lon2: Longitude = Longitude(degree=-91, minute=-47, second=0)  # -91.783333
pylon2: LatLon = LatLon(lat2, lon2)

# Takeoff Position set in takeoff.py
takeoff_pos = LatLon

# Position for the mast
MAST_LAT: Latitude = Latitude(
    37.9486054
)  # degree=37, minute=56, second=53.0)  # 37.948056 placeholder
MAST_LON: Longitude = Longitude(
    -91.7843514
)  # degree=-91, minute=-47, second=-5.0)  # -91.784722
MAST_LOCATION: LatLon = LatLon(MAST_LAT, MAST_LON)
# flight test lat: 37.9486054, lon: -91.7843514


OFFSET_RIGHT = {"KM": 0.005, "DEG": 90}
OFFSET_LEFT = {"KM": 0.005, "DEG": -90}
OFFSET_BACK = {"KM": 0.005, "DEG": 180}
OFFSET_FRONT = {"KM": 0.005, "DEG": 0}
OFFSET_NONE = {"KM": 0, "DEG": 0}

THINK_FOR_S: float = 2.0
FAST_THINK_S: float = 1.0
MAST_WAIT_TIME: float = 5

REALSENSE_WIDTH: int = 1920
REALSENSE_HEIGHT: int = 1080
REALSENSE_FRAMERATE: int = 60


async def config_params(drone: System):
    await drone.action.set_maximum_speed(MAX_SPEED)
    await drone.param.set_param_float("MIS_TAKEOFF_ALT", TAKEOFF_ALT)
    await drone.action.set_maximum_speed(MAX_SPEED)
    await drone.param.set_param_float("MPC_XY_VEL_MAX", MAX_SPEED)
    await drone.param.set_param_float("MPC_XY_CRUISE", MAX_SPEED)

    # Set data link loss failsafe mode HOLD
    await drone.param.set_param_int("NAV_DLL_ACT", 1)
    # Set offboard loss failsafe mode HOLD
    await drone.param.set_param_int("COM_OBL_ACT", 1)
    # Set offboard loss failsafe mode when RC is available HOLD
    await drone.param.set_param_int(
        "COM_OBL_RC_ACT", 5
    )  # Set RC loss failsafe mode HOLD
    await drone.param.set_param_int("NAV_RCL_ACT", 1)
