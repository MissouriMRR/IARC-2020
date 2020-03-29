from flight.utils.latlon.lat_lon import Latitude, Longitude, LatLon
import asyncio
from mavsdk import System



MAX_SPEED: float =6.352 #m/s
ALT_CORRECTION_SPEED: float = 0.25 #m/s down
MAX_ALT: float = 9.0 #m
TAKEOFF_ALT: float = 6.0 #m
# What percentage of the hight can we loos/gain before unsafe
ALT_PERCENT_ACCURACY: float = 0.15 
ALT_RANGE_MAX: float = TAKEOFF_ALT+(TAKEOFF_ALT*ALT_PERCENT_ACCURACY) #m
ALT_RANGE_MIN: float = TAKEOFF_ALT-(TAKEOFF_ALT*ALT_PERCENT_ACCURACY) #m

POINT_PERCENT_ACCURACY: float = 0.2

# Position for pylon 1
lat1: Latitude = Latitude(degree=37, minute=56, second=55.6)
lon1: Longitude = Longitude(degree=-91, minute=-47, second=-3.3)
pylon1: LatLon = LatLon(lat1, lon1)

# Position for pylon 2
#lat2: float = 37.9486433
#lon2: float = -91.7839372
#lat2: float = 37.9481946
#lon2: float = -91.7834122
lat2: Latitude = Latitude(degree=37, minute=56, second=53.3)
lon2: Longitude = Longitude(degree=-91, minute=-47, second=0)
pylon2: LatLon = LatLon(lat2, lon2)

OFFSET: float = .005 #km
DEG_OFFSET: int = 90 #deg

NUM_LAPS: int = 2



async def config_param(drone: System):
    await drone.param.set_float_param('MIS_TAKEOFF_ALT', TAKEOFF_ALT)
    await drone.param.set_float_param('MPC_CRUISE_90', MAX_SPEED)
    await drone.param.set_float_param('MPC_XY_VEL_MAX', MAX_SPEED)
    await drone.param.set_float_param('MPC_XY_CRUISE', MAX_SPEED)
    await drone.action.set_maximum_speed(MAX_SPEED)
    #Set data link loss failsafe mode HOLD
    await drone.param.set_int_param('NAV_DLL_ACT', 1)
    #Set offboard loss failsafe mode HOLD
    await drone.param.set_int_param('COM_OBL_ACT', 1)
    #Set offboard loss failsafe mode when RC is available HOLD
    await drone.param.set_int_param('COM_OBL_RC_ACT', 5)

    #Set RC loss failsafe mode HOLD
    await drone.param.set_int_param('NAV_RCL_ACT', 1)

    await drone.param.set_float_param('LNDMC_XY_VEL_MAX', .5)
    await drone.param.set_float_param('LNDMC_FFALL_THR', 3)
    await drone.param.set_float_param('LNDMC_FFALL_TTRI', .15)
    await drone.param.set_float_param('LNDMC_ALT_MAX', MAX_ALT)
    await drone.param.set_float_param('LNDMC_LOW_T_THR', .2)
    

    return
        

#COM_OBL_ACT* 0
#COM_OBL_RC_ACT* 0
#COM_RC_OVERRIDE
#GPS_DUMP_COMM
#NAV_DLL_ACT* 0
#NAV_RCL_ACT* 2
#MC_AIRMODE

#COM_POSCTL_NAVL-
#LNDMC_ALT_MAX 
#LNDMC_FFALL_THR free-fall detection m/s^2  2
#LNDMC_FFALL_TTRI Multicopter free-fall trigger time s .3
#LNDMC_XY_VEL_MAX  m/s 1.5
#LNDMC_Z_VEL_MAX 
#LNDMC_LOW_T_THR Low throttle detection threshold .3
#MAV_0_MODE
#MAV_0_RATE 

#EKF2
#Local position Estimator
#SD Logging
#Landing target Estimator

