'''
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
'''

'''
Imports
'''

from lac import LAC
import time

'''
Constants
'''
#Default IDs
vendorID = 0x4D8
productID= 0xFC5F

#Retract
rLimit = 1 #Retract limit
rPosition = 1 #Ideal retract position
rMechStop = 0 #Mechanical stop of retract

#Extend
eLimit = 1022 #Extend limit
ePosition = 1022 #Ideal extend position
eMechStop = 1023 #Mechanical stop of extend

#Additional Values
maxPWM = 1022
minPWM = 1
stallTime = 1000 #1000ms (1 second)
moveThresh = 5 #Movement threshold
accVal = 4 #Accuracy value
maxSpeed = 1022
sleepVal = 6 #6 seconds
stroke = 300 #max length of LAC (mm)


class sLAC:
  def __init__(self):
    self.piston = LAC(vendorID,productID)
    self.setupLAC()
    
    #Ensures the LAC will not hit mechanical stops
    if (rPosition <= rMechStop):
      raise Exception("Retract is set to the mechanical stop.")
    elif (ePosition >= eMechStop):
      raise Exception("Extend is set to the mechanical stop.")
  
  #Automatically sets up the LAC
  def setupLAC(self):
    
    #Retract limit set to 1mm (0-1023)
    self.piston.set_retract_limit(rLimit)
    print("Retract limit set")
    
    #Extend limit set to 1022mm (0-1023)
    self.piston.set_extend_limit(eLimit)
    print("Extend limit set")
    
    #How close to target is acceptable
    self.piston.set_accuracy(accVal)
    print("Accuracy set")
    
    #Min speed (mm/s) before stalling
    self.piston.set_movement_threshold(moveThresh)
    print("Movement Threshold set")
  
    #Stall time (ms) set to 1 second
    self.piston.set_stall_time(stallTime)
    print("Stall Time set")
  
    #[1,1022]
    self.piston.set_max_pwm_value(maxPWM)
    print("Max PWM set")
  
    #[1,1022]
    self.piston.set_min_pwm_value(minPWM)
    print("Min PWM set")
  
    #Keep on max speed [1,1022]
    self.piston.set_speed(maxSpeed)
    print("Piston set to max speed")
    
    

  #Extends the LAC to the max value without hitting mechanical stop
  #Takes 5 seconds to fully extend
  def extendLAC(self):
    print("Extending...")
    self.piston.set_position(eLimit)
    time.sleep(sleepVal) #Wait 6.5 seconds during extension
    
  #Retracts the LAC to the max value without hitting mechanical stop
  #Takes 5 seconds to fully retract
  def retractLAC(self):
    self.piston.set_position(rLimit)
    time.sleep(sleepVal) #Wait 6.5 seconds during retraction

  #Returns the current location of the LAC from [rLimit, eLimit]
  #Prints the metric location (mm) of LAC
  def positionLAC(self):
    actualPos = int(self.piston.get_feedback()) #Actual 2-bit position
    distance = (actualPos * stroke)/eLimit #Calculate metric distance
    print(str(distance) + "mm")
    return actualPos
  
  #Retracts LAC to the original position
  #Factory reset to solve stalling issue
  def resetLAC(self):
    print("Resetting...")
    self.retractLAC()
    self.piston.reset()


