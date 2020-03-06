from flight.utils.latlon import LatLon
import asyncio
from mavsdk import System

class Constant:
    MAX_SPEED: float =2.352 #m/s
    ALT_CORRECTION_SPEED: float = 0.25 #m/s down
    MAX_ALT: float = 15.0 #m
    TAKEOFF_ALT: float = 3.0 #m
    #what percentage of the hight can we loos/gain before unsafe
    ALT_PERCENT_ACCURACY: float = 0.25 
    ALT_RANGE_MAX: float = TAKEOFF_ALT+(TAKEOFF_ALT*ALT_PERCENT_ACCURACY) #m
    ALT_RANGE_MIN: float = TAKEOFF_ALT-(TAKEOFF_ALT*ALT_PERCENT_ACCURACY) #m

    POINT_PERCENT_ACCURACY: float = 0.25

    # Position for pylon 1
    lat1: float = 37.9489551
    lon1: float = -91.7844405
    pylon1: LatLon = LatLon(lat1, lon1)

    # Position for pylon 2
    lat2: float = 37.9486433
    lon2: float = -91.7839372
    pylon2: LatLon = LatLon(lat2, lon2)



    async def config_param(self, drone: System):
        await drone.param.set_float_param('MIS_TAKEOFF_ALT', TAKEOFF_ALT)
        await drone.param.set_float_param('MPC_CRUISE_90', MAX_SPEED)
        await drone.param.set_float_param('MPC_XY_VEL_MAX', MAX_SPEED)
        await drone.param.set_float_param('MPC_XY_CRUISE', MAX_SPEED)
        await drone.action.set_maximum_speed(MAX_SPEED)
        pass

#COM_OBL_ACT
#COM_OBL_RC_ACT
#COM_RC_OVERRIDE
#GPS_DUMP_COMM
#NAV_DLL_ACT
#NAV_RCL_ACT
#MC_AIRMODE

#EKF2
#Local position Estimator
#SD Logging
#Landing target Estimator

