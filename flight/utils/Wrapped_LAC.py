"""Imports"""
from .lac import LAC
import time
import logging

"""
Given:
  Distance = value/1024 * stroke
  Stroke is max extension length
  All values in mm
  0 and 1023 are the mechanical stops **BAD**
  Max Speed = 46 mm/s
  Stroke = 300mm

Notes:
  DO NOT set the rLimit or eLimit to their respective mechanical stops
    (Unless you want to possibly break the Linear Actuator)

  Functions not used in our Actuonix Linear Actuator from 'lac.py':
    linearActuator.set_proportional_gain()
    linearActuator.set_derivative_gain()
    linearActuator.disable_manual() DONT TOUCH THIS PL0x

    Both of these didn't do anything when tested:
      piston.set_average_rc(?) [0, 1024]
      piston.set_average_adc(?) [0, 1024]
"""

"""Constants"""
# Default IDs
vendorID = 0x4D8
productID = 0xFC5F

# Retract
rLimit = 1  # Retract limit
rPosition = 1  # Ideal retract position
rMechStop = 0  # Mechanical stop of retract

# Extend
eLimit = 1022  # Extend limit
ePosition = 1022  # Ideal extend position
eMechStop = 1023  # Mechanical stop of extend

# Additional Values
maxPWM = 1022
minPWM = 1
stallTime = 1000  # 1000ms (1 second)
moveThresh = 5  # Movement threshold
accVal = 4  # Accuracy value
maxSpeed = 1022
sleepVal = 6  # 6 seconds
stroke = 300  # max length of LAC (mm)


class sLAC:
    """
    Control for the linear actuator

    Attributes:
        piston: object for movement action in the class
    Functions:
        __init__: Initializes LAC as to not hit mechanical stops in motion
        setupLAC: Sets up LAC with constant values
        extendLAC: Extends LAC to maximum values
        retractLAC: Retracts LAC to maximum values
        positionLAC: Returns and prints the current location of the LAC
        resetLAC: Retracts the LAC to original starting position
    """

    def __init__(self):
        """
        Initializes LAC as to not hit mechanical stops

        Parameters:
            N/A
        Return:
            None
        Logging:
            To error; failure to connect to the piston of the LAC
        Raises:
            Exception: If the extension/retraction is set to be the mechanical stop
        """
        # Ensures the LAC will not hit mechanical stops
        if rPosition <= rMechStop:
            raise Exception("Retract is set to the mechanical stop.")
        elif ePosition >= eMechStop:
            raise Exception("Extend is set to the mechanical stop.")

        try:
            self.piston = LAC(vendorID, productID)
            self.setupLAC()
        except Exception:
            logging.error("Failed to connect to the piston")

    def setupLAC(self) -> None:
        """
        Automatically sets up the LAC

        Parameters:
            N/A
        Return:
            None
        Logging:
            N/A
        """
        # Retract limit set to 1mm (0-1023)
        self.piston.set_retract_limit(rLimit)
        print("Retract limit set")

        # Extend limit set to 1022mm (0-1023)
        self.piston.set_extend_limit(eLimit)
        print("Extend limit set")

        # How close to target is acceptable
        self.piston.set_accuracy(accVal)
        print("Accuracy set")

        # Min speed (mm/s) before stalling
        self.piston.set_movement_threshold(moveThresh)
        print("Movement Threshold set")

        # Stall time (ms) set to 1 second
        self.piston.set_stall_time(stallTime)
        print("Stall Time set")

        # [1,1022]
        self.piston.set_max_pwm_value(maxPWM)
        print("Max PWM set")

        # [1,1022]
        self.piston.set_min_pwm_value(minPWM)
        print("Min PWM set")

        # Keep on max speed [1,1022]
        self.piston.set_speed(maxSpeed)
        print("Piston set to max speed")

    def extendLAC(self) -> None:
        """
        Extends the LAC to the max values without hitting the mechanical stops
        Takes 5 seconds to fully extend

        Parameters:
            N/A
        Return:
            None
        Logging:
            N/A
        """
        print("Extending...")
        if self.piston:
            self.piston.set_position(eLimit)
        time.sleep(sleepVal)  # Wait 6.5 seconds during extension

    def retractLAC(self) -> None:
        """
        Retracts LAC to the max value without hitting the mechanical stop
        Takes 5 seconds to fully retract

        Parameters:
            N/A
        Return:
            None
        Logging:
            N/A
        """
        if self.piston:
            self.piston.set_position(rLimit)
        time.sleep(sleepVal)  # Wait 6.5 seconds during retraction

    def positionLAC(self):
        """
        Returns the current location of the LAC from [rLimit, eLimit], and prints the metric
        location (mm) of the LAC

        Parameters:
            N/A
        Return:
            actualPos (int): 2-bit position of the piston
        Logging:
            N/A
        """
        if self.piston is None:
            return -1
        actualPos = int(self.piston.get_feedback())  # Actual 2-bit position
        distance = (actualPos * stroke) / eLimit  # Calculate metric distance
        print(str(distance) + "mm")
        return actualPos

    def resetLAC(self) -> None:
        """
        Retracts the LAC to its original position
        Factory reset to solve stalling issues

        Parameters:
            N/A
        Return:
            None
        Logging:
           N/A
        """
        print("Resetting...")
        self.retractLAC()
        if self.piston:
            self.piston.reset()
