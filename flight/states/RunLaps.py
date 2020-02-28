import asyncio
import math
import mavsdk as sdk
from .Land import Land

lat1: int = 37.9489551
lon1: int = -91.7844405
lat2: int = 37.9486433
lon2: int = -91.7839372


async def arange(count):
    for i in range(count):
        yield (i)


class RunLaps:
    async def run(self, drone):

        print("-- Run Laps")
        pos_wait = asyncio.ensure_future(self.wait_pos(drone, lat1, lon1))
        await pos_wait
        pos_wait.cancel()
        del pos_wait
        async for i in arange(8):
            print(f"STARTING LAP {i}")
            pos_wait = asyncio.ensure_future(self.wait_pos(drone, lat2, lon2))
            await pos_wait
            pos_wait.cancel()
            del pos_wait

            turn = asyncio.ensure_future(self.wait_turn(drone))
            await turn
            turn.cancel()
            del turn

            pos_wait = asyncio.ensure_future(self.wait_pos(drone, lat1, lon1))
            await pos_wait

            pos_wait.cancel()
            del pos_wait

            turn = asyncio.ensure_future(self.wait_turn(drone))
            await turn
            turn.cancel()
            del turn
        return Land()

    async def wait_pos(self, drone, goal_lat, goal_lon):

        async for gps in drone.telemetry.position():
            altitude = round(gps.relative_altitude_m, 2)
            if altitude >= 12:
                alt = 0.25
            elif altitude <= 9:
                alt = -0.25
            else:
                alt = 0
            lat = round(gps.latitude_deg, 8)
            lon = round(gps.longitude_deg, 8)
            x = (
                (goal_lon - lon)
                * 40000
                * math.cos((goal_lat + lat) * math.pi / 360)
                / 360
            ) * 1000
            y = ((goal_lat - lat) * 40000 / 360) * 1000

            try:  # calcualte what degree to point at
                deg = round((((math.atan(x / y) / math.pi) * 180)))

                if y < 0:
                    z = 180
                    z = math.copysign(z, deg)
                    deg = z + deg
            except ZeroDivisionError:
                deg = round(
                    (
                        (
                            (math.asin(x / (math.sqrt((x ** 2) + (y ** 2)))) / math.pi)
                            * 180
                        )
                    )
                )

                if y < 0:
                    z = 180
                    deg = -deg
                    z = math.copysign(z, deg)
                    deg = z + deg

            try:  # deturman what velocity should go at
                dx = math.copysign(35 * math.cos(math.atan(y / x)), x)
                dy = math.copysign(35 * math.sin(math.atan(y / x)), y)

            except ZeroDivisionError:
                dx = math.copysign(
                    35 * math.cos(math.asin(y / (math.sqrt((x ** 2) + (y ** 2))))), x
                )
                dy = math.copysign(
                    35 * math.sin(math.asin(y / (math.sqrt((x ** 2) + (y ** 2))))), y
                )

            await drone.offboard.set_velocity_ned(sdk.VelocityNedYaw(dy, dx, alt, deg))

            if abs(x) <= 10 and abs(y) <= 10:
                return True

    async def wait_turn(self, drone):

        count = 0
        async for tel in drone.telemetry.attitude_euler():
            current = (360 + round(tel.yaw_deg)) % 360
            if count == 0:
                temp = (current + 180) % 360

            await drone.offboard.set_velocity_body(
                sdk.VelocityBodyYawspeed(60, -55, 0.25, -90)
            )
            if current == temp:
                return True
            count += 1
