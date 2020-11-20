"""Sets parameters for the drone and holds constant values needed for configuration"""
from flight.utils.latlon import LatLon, Latitude, Longitude

from mavsdk import System


MAX_SPEED: float = 6.352  # m/s
ALT_CORRECTION_SPEED: float = 0.25  # m/s down
MAX_ALT: float = 9.0  # m
TAKEOFF_ALT: float = 1.0  # m
FLYING_ALT: float = 6.0  # m
# What percentage of the hight can we loos/gain before unsafe
ALT_PERCENT_ACCURACY: float = 0.15
ALT_RANGE_MAX: float = FLYING_ALT + (FLYING_ALT * ALT_PERCENT_ACCURACY)  # m
ALT_RANGE_MIN: float = FLYING_ALT - (FLYING_ALT * ALT_PERCENT_ACCURACY)  # m

POINT_PERCENT_ACCURACY: float = 0.2

# Position for pylon 1
# lat1: Latitude = Latitude(37.9497800)
# lon1: Longitude = Longitude(-92.7854470)
lat1: Latitude = Latitude(degree=37, minute=56, second=55.6)
lon1: Longitude = Longitude(degree=-91, minute=-47, second=-3.3)
pylon1: LatLon = LatLon(lat1, lon1)

# Position for pylon 2
# lat2: float = 37.9486433
# lon2: float = -91.7839372
# lat2: float = Latitude(37.9504260)
# lon2: float = Longitude(-91.7848542)

lat2: Latitude = Latitude(degree=37, minute=56, second=53.3)
lon2: Longitude = Longitude(degree=-91, minute=-47, second=0)
pylon2: LatLon = LatLon(lat2, lon2)

# Position for the mast
MAST_LAT: Latitude = Latitude(degree=37, minute=56, second=53.0) # placeholder postion
MAST_LON: Longitude = Longitude(degree=-91, minute=-47, second=-5.0)
MAST_LOCATION: LatLon = LatLon(MAST_LAT, MAST_LON)

OFFSET: float = 0.005  # km
DEG_OFFSET: int = 90  # deg

NUM_LAPS: int = 2

THINK_FOR_S: float = 2.0
FAST_THINK_S: float = 1.0


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
    await drone.param.set_param_int("COM_OBL_RC_ACT", 5)

    # Set RC loss failsafe mode HOLD
    await drone.param.set_param_int("NAV_RCL_ACT", 1)
    await drone.param.set_param_float("LNDMC_XY_VEL_MAX", 0.5)
    # await drone.param.set_param_float("LNDMC_FFALL_THR", 3)
    # await drone.param.set_param_float("LNDMC_FFALL_TTRI", 0.15)
    await drone.param.set_param_float("LNDMC_ALT_MAX", MAX_ALT)
    # await drone.param.set_param_float("LNDMC_LOW_T_THR", 0.2)
