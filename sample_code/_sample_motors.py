from utils.brick import Motor
import time
other_motor = Motor("C")


motor = Motor("A")


### Power ###
motor.set_power(100) # 100%
# OR
motor.set_power(-50) # Backwards 50%
# OR
motor.set_power(0)   # Stops motor. Motor cannot rotate.

### Speed ###
motor.set_dps(90) # 90 deg/sec
# OR
motor.set_dps(-720) # Backwards 720 deg/sec
# OR
motor.set_dps(0)    # Stops motor. Motor cannot rotate.

from utils.brick import Motor
import time
other_motor = Motor("C")

# Designates to Encoder, that the current physical position is 0 degrees
other_motor.reset_encoder()

# Rotate to position that is 720 degrees away from the 0 position
other_motor.set_position(720)
time.sleep(2) # Wait to finish
other_motor.set_position(720) # This does nothing, because we are here
other_motor.set_position(700) # Move backwards 20 degrees
time.sleep(1)

# Returns the current position for you. So you know where you are.
other_motor.get_position() 


# Prevents position control from going over either:
# 50% power or 90 deg/sec, whichever is slower
other_motor.set_limits(power=50, dps=90)

other_motor.set_limits(power=50) # Limit one only, don't care about other
other_motor.set_limits() # UNLIMITED POWER (AND SPEED)

# Will rotate 180 degrees backwards from current position.
# Does not care about the absolute position.
other_motor.set_position_relative(-180)
time.sleep(2)


