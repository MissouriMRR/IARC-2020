from flight.utils.latlon import LatLon
import asyncio
from mavsdk import System


class Constant:
    def __init__(self):
        self.MAX_SPEED: float = 2.352  # m/s
        self.ALT_CORRECTION_SPEED: float = 0.25  # m/s down
        self.MAX_ALT: float = 15.0  # m
        self.TAKEOFF_ALT: float = 3.0  # m
        # What percentage of the hight can we loos/gain before unsafe
        self.ALT_PERCENT_ACCURACY: float = 0.25
        self.ALT_RANGE_MAX: float = self.TAKEOFF_ALT + (
            self.TAKEOFF_ALT * self.ALT_PERCENT_ACCURACY
        )  # m
        self.ALT_RANGE_MIN: float = self.TAKEOFF_ALT - (
            self.TAKEOFF_ALT * self.ALT_PERCENT_ACCURACY
        )  # m

        self.POINT_PERCENT_ACCURACY: float = 0.1

        # Position for pylon 1
        self.lat1: float = 37.9489551
        self.lon1: float = -91.7844405
        self.pylon1: LatLon = LatLon(self.lat1, self.lon1)

        # Position for pylon 2
        self.lat2: float = 37.9486433
        self.lon2: float = -91.7839372
        self.pylon2: LatLon = LatLon(self.lat2, self.lon2)

    async def config_param(self, drone: System):
        await drone.param.set_float_param("MIS_TAKEOFF_ALT", self.TAKEOFF_ALT)
        await drone.param.set_float_param("MPC_CRUISE_90", self.MAX_SPEED)
        await drone.param.set_float_param("MPC_XY_VEL_MAX", self.MAX_SPEED)
        await drone.param.set_float_param("MPC_XY_CRUISE", self.MAX_SPEED)
        await drone.action.set_maximum_speed(self.MAX_SPEED)
        # Set data link loss failsafe mode HOLD
        await drone.param.set_int_param("NAV_DLL_ACT", 1)
        # Set RC loss failsafe mode HOLD
        # await drone.param.set_int_param('NAV_RCL_ACT', 1)
        # Set offboard loss failsafe mode HOLD
        await drone.param.set_int_param("COM_OBL_ACT", 1)
        # Set offboard loss failsafe mode when RC is available HOLD
        await drone.param.set_int_param("COM_OBL_RC_ACT", 5)
        return


# COM_OBL_ACT*
# COM_OBL_RC_ACT*
# COM_RC_OVERRIDE
# GPS_DUMP_COMM
# NAV_DLL_ACT*
# NAV_RCL_ACT*
# MC_AIRMODE

# EKF2
# Local position Estimator
# SD Logging
# Landing target Estimator

