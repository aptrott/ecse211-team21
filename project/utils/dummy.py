from math import inf
import threading
from typing import Literal
import time


class Enumeration(object):
    def __init__(self, names):  # or *names, with no .split()
        number = 0
        for line, name in enumerate(names.split('\n')):
            if name.find(",") >= 0:
                # strip out the spaces
                while(name.find(" ") != -1):
                    name = name[:name.find(" ")] + name[(name.find(" ") + 1):]

                # strip out the commas
                while(name.find(",") != -1):
                    name = name[:name.find(",")] + name[(name.find(",") + 1):]

                # if the value was specified
                if(name.find("=") != -1):
                    number = int(float(name[(name.find("=") + 1):]))
                    name = name[:name.find("=")]

                # optionally print to confirm that it's working correctly
                # print "%40s has a value of %d" % (name, number)

                setattr(self, name, number)
                number = number + 1


class FirmwareVersionError(Exception):
    """Exception raised if the BrickPi3 firmware needs to be updated"""


class SensorError(Exception):
    """Exception raised if a sensor is not yet configured when trying to read it with get_sensor"""


class _FakeMotor:
    MAX_SPEED = 1050
    MAX_POS = 65536
    THREAD_INTERVAL = 0.2

    def __init__(self):
        self.event = threading.Event()
        self.thread = threading.Thread(target=self._listener, daemon=True)

        self.position_goal = None
        self.state = 0

        self.position = 0
        self.speed = 0  # Maximum is 1050dps
        self.power = 0  # Maximum is 1050dps

        self.set_limits()

    def start(self):
        self.event.set()
        self.thread.start()

    @staticmethod
    def limit(val, lower, upper):
        return min(max(val, lower), upper)

    @staticmethod
    def abs_limit(val, limit):
        limit = abs(limit)
        return _FakeMotor.limit(val, -limit, limit)

    def _listener(self, *args):
        while self.event.is_set():
            if self.position_goal is not None:
                if self.state == 0:
                    self.state = -1 if self.position_goal < self.position else 1
                best_speed = self.state * min(self.speed_limit,
                                         self.power_limit/100*self.MAX_SPEED)
                self.speed = best_speed
                self.power = best_speed * 100 / self.MAX_SPEED

                if (self.state == -1 and self.position <= self.position_goal) or (self.state == 1 and self.position >= self.position_goal):
                    self.set_position(self.position_goal)
                    self.position_goal = None
                    self.state = 0
                    self.speed = 0
                    self.power = 0
            else:
                self.state = 0
            delta_pos = self.speed * self.THREAD_INTERVAL
            self.set_position(self.position + delta_pos)
            time.sleep(self.THREAD_INTERVAL)

    def go_position(self, goal):
        self.stop()
        self.position_goal = self.abs_limit(goal, self.MAX_POS)

    def stop(self):
        self.speed = 0
        self.power = 0
        self.state = 0
        self.position_goal = None

    def power_to_speed(self):
        self.speed = self.power / 100 * self.MAX_SPEED

    def speed_to_power(self):
        self.power = self.speed / self.MAX_SPEED * 100

    def set_limits(self, power=0, speed=0):
        power = abs(power)
        speed = abs(speed)
        if power == 0:
            self.power_limit = 100
        else:
            self.power_limit = self.limit(power, 0, 100)
        if speed == 0:
            self.speed_limit = self.MAX_SPEED
        else:
            self.speed_limit = self.limit(speed, 0, self.MAX_SPEED)

    def set_power(self, power):
        self.stop()
        self.power = power
        self.power_to_speed()

    def set_speed(self, speed):
        self.stop()
        self.speed = speed
        self.speed_to_power()

    def set_position(self, pos):
        if pos is None:
            self.position = 0
        self.position = round((self.abs_limit(pos, self.MAX_POS) +
                               self.MAX_POS) % (131072+1) - self.MAX_POS, 1)

    def shutdown(self):
        self.event.clear()

    def __del__(self):
        self.shutdown()


class BrickPi3():
    PORT_1 = 0x01
    PORT_2 = 0x02
    PORT_3 = 0x04
    PORT_4 = 0x08

    PORT_A = 0x01
    PORT_B = 0x02
    PORT_C = 0x04
    PORT_D = 0x08

    MOTOR_FLOAT = -128

    SensorType = [0, 0, 0, 0]
    I2CInBytes = [0, 0, 0, 0]

    I2C_LENGTH_LIMIT = 16

    BPSPI_MESSAGE_TYPE = Enumeration("""
        NONE,

        GET_MANUFACTURER,
        GET_NAME,
        GET_HARDWARE_VERSION,
        GET_FIRMWARE_VERSION,
        GET_ID,
        SET_LED,
        GET_VOLTAGE_3V3,
        GET_VOLTAGE_5V,
        GET_VOLTAGE_9V,
        GET_VOLTAGE_VCC,
        SET_ADDRESS,

        SET_SENSOR_TYPE,

        GET_SENSOR_1,
        GET_SENSOR_2,
        GET_SENSOR_3,
        GET_SENSOR_4,

        I2C_TRANSACT_1,
        I2C_TRANSACT_2,
        I2C_TRANSACT_3,
        I2C_TRANSACT_4,

        SET_MOTOR_POWER,

        SET_MOTOR_POSITION,

        SET_MOTOR_POSITION_KP,

        SET_MOTOR_POSITION_KD,

        SET_MOTOR_DPS,

        SET_MOTOR_DPS_KP,

        SET_MOTOR_DPS_KD,

        SET_MOTOR_LIMITS,

        OFFSET_MOTOR_ENCODER,

        GET_MOTOR_A_ENCODER,
        GET_MOTOR_B_ENCODER,
        GET_MOTOR_C_ENCODER,
        GET_MOTOR_D_ENCODER,

        GET_MOTOR_A_STATUS,
        GET_MOTOR_B_STATUS,
        GET_MOTOR_C_STATUS,
        GET_MOTOR_D_STATUS,
    """)

    SENSOR_TYPE = Enumeration("""
        NONE = 1,
        I2C,
        CUSTOM,

        TOUCH,
        NXT_TOUCH,
        EV3_TOUCH,

        NXT_LIGHT_ON,
        NXT_LIGHT_OFF,

        NXT_COLOR_RED,
        NXT_COLOR_GREEN,
        NXT_COLOR_BLUE,
        NXT_COLOR_FULL,
        NXT_COLOR_OFF,

        NXT_ULTRASONIC,

        EV3_GYRO_ABS,
        EV3_GYRO_DPS,
        EV3_GYRO_ABS_DPS,

        EV3_COLOR_REFLECTED,
        EV3_COLOR_AMBIENT,
        EV3_COLOR_COLOR,
        EV3_COLOR_RAW_REFLECTED,
        EV3_COLOR_COLOR_COMPONENTS,

        EV3_ULTRASONIC_CM,
        EV3_ULTRASONIC_INCHES,
        EV3_ULTRASONIC_LISTEN,

        EV3_INFRARED_PROXIMITY,
        EV3_INFRARED_SEEK,
        EV3_INFRARED_REMOTE,
    """)

    SENSOR_STATE = Enumeration("""
        VALID_DATA,
        NOT_CONFIGURED,
        CONFIGURING,
        NO_DATA,
        I2C_ERROR,
    """)

    SENSOR_CUSTOM = Enumeration("""
        PIN1_9V,
        PIN5_OUT,
        PIN5_STATE,
        PIN6_OUT,
        PIN6_STATE,
        PIN1_ADC,
        PIN6_ADC,
    """)
    """
    Flags for use with SENSOR_TYPE.CUSTOM

    PIN1_9V
        Enable 9V out on pin 1 (for LEGO NXT Ultrasonic sensor).

    PIN5_OUT
        Set pin 5 state to output. Pin 5 will be set to input if this flag is not set.

    PIN5_STATE
        If PIN5_OUT is set, this will set the state to output high, otherwise the state will
        be output low. If PIN5_OUT is not set, this flag has no effect.

    PIN6_OUT
        Set pin 6 state to output. Pin 6 will be set to input if this flag is not set.

    PIN6_STATE
        If PIN6_OUT is set, this will set the state to output high, otherwise the state will
        be output low. If PIN6_OUT is not set, this flag has no effect.

    PIN1_ADC
        Enable the analog/digital converter on pin 1 (e.g. for NXT analog sensors).

    PIN6_ADC
        Enable the analog/digital converter on pin 6.
    """

    SENSOR_CUSTOM.PIN1_9V = 0x0002
    SENSOR_CUSTOM.PIN5_OUT = 0x0010
    SENSOR_CUSTOM.PIN5_STATE = 0x0020
    SENSOR_CUSTOM.PIN6_OUT = 0x0100
    SENSOR_CUSTOM.PIN6_STATE = 0x0200
    SENSOR_CUSTOM.PIN1_ADC = 0x1000
    SENSOR_CUSTOM.PIN6_ADC = 0x4000

    SENSOR_I2C_SETTINGS = Enumeration("""
        MID_CLOCK,
        PIN1_9V,
        SAME,
        ALLOW_STRETCH_ACK,
        ALLOW_STRETCH_ANY,
    """)

    # Send the clock pulse between reading and writing. Required by the NXT US sensor.
    SENSOR_I2C_SETTINGS.MID_CLOCK = 0x01
    SENSOR_I2C_SETTINGS.PIN1_9V = 0x02  # 9v pullup on pin 1
    # Keep performing the same transaction e.g. keep polling a sensor
    SENSOR_I2C_SETTINGS.SAME = 0x04

    MOTOR_STATUS_FLAG = Enumeration("""
        LOW_VOLTAGE_FLOAT,
        OVERLOADED,
    """)

    # If the motors are floating due to low battery voltage
    MOTOR_STATUS_FLAG.LOW_VOLTAGE_FLOAT = 0x01
    # If the motors aren't close to the target (applies to position control and dps speed control).
    MOTOR_STATUS_FLAG.OVERLOADED = 0x02

    #SUCCESS = 0
    #SPI_ERROR = 1
    #SENSOR_ERROR = 2
    #SENSOR_TYPE_ERROR = 3

    @classmethod
    def _convert_port(cls, port):
        if port == cls.PORT_1:
            message_type = cls.BPSPI_MESSAGE_TYPE.GET_SENSOR_1
            port_index = 0
        elif port == cls.PORT_2:
            message_type = cls.BPSPI_MESSAGE_TYPE.GET_SENSOR_2
            port_index = 1
        elif port == cls.PORT_3:
            message_type = cls.BPSPI_MESSAGE_TYPE.GET_SENSOR_3
            port_index = 2
        elif port == cls.PORT_4:
            message_type = cls.BPSPI_MESSAGE_TYPE.GET_SENSOR_4
            port_index = 3
        else:
            raise IOError(
                "get_sensor error. Must be one sensor port at a time. PORT_1, PORT_2, PORT_3, or PORT_4.")
        return (port_index, message_type)

    def __init__(self, addr=1, detect=True):
        self.SPI_Address = 1
        self.SensorType = [None for i in range(4)]
        self.Motors = [_FakeMotor() for i in range(4)]
        self.SPI_Messages = {self._convert_port(2**i)[1]: i for i in range(4)}
        for mot in self.Motors:
            mot.start()

        self._internal_data = {
            BrickPi3.SENSOR_TYPE.TOUCH: 0,
            BrickPi3.SENSOR_TYPE.EV3_ULTRASONIC_CM: 255.0,
            BrickPi3.SENSOR_TYPE.EV3_ULTRASONIC_INCHES: 100.0,
            BrickPi3.SENSOR_TYPE.EV3_ULTRASONIC_LISTEN: 0,
            BrickPi3.SENSOR_TYPE.EV3_COLOR_COLOR_COMPONENTS: (0, 0, 0, 0),
            BrickPi3.SENSOR_TYPE.EV3_COLOR_AMBIENT: (0, 0, 0, 0),
            BrickPi3.SENSOR_TYPE.EV3_COLOR_REFLECTED: 0,
            BrickPi3.SENSOR_TYPE.EV3_COLOR_RAW_REFLECTED: 0,
            BrickPi3.SENSOR_TYPE.EV3_COLOR_COLOR: 0,
            BrickPi3.SENSOR_TYPE.EV3_GYRO_ABS: 0,
            BrickPi3.SENSOR_TYPE.EV3_GYRO_DPS: 0,
            BrickPi3.SENSOR_TYPE.EV3_GYRO_ABS_DPS: (0, 0)
        }

    def __del__(self):
        for mot in self.Motors:
            mot.shutdown()

    def spi_transfer_array(self, data_out):
        """Used by Brick.get_sensor_status"""
        """
        [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0, 0, 0]
        => [0,0,0,0xA5,self.SensorType[i],status]

        [self.SPI_Address, message_type, 0, 0, 0, 0]
        => [0,0,0,0xA5,self.SensorType[i],status]

        [self.SPI_Address, message_type, 0, 0, 0, 0, 0]
        => [0,0,0,0xA5,self.SensorType[i],status]

        [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        => [0,0,0,0xA5,self.SensorType[i],status]
        """
        SENSOR_STATUS = 0  # Valid Data
        BAD_REPLY = [0, 0, 0, 0, 0, 0]

        data = list(data_out)
        if len(data) < 2:
            return BAD_REPLY

        i = self.SPI_Messages.get(data[1], -1)
        GOOD_REPLY = [0, 0, 0, 0xA5, self.SensorType[i], SENSOR_STATUS]

        return GOOD_REPLY

    def spi_write_8(self, MessageType, Value):
        pass

    def spi_read_16(self, MessageType):
        pass

    def spi_write_16(self, MessageType, Value):
        pass

    def spi_write_24(self, MessageType, Value):
        pass

    def spi_read_32(self, MessageType):
        pass

    def spi_write_32(self, MessageType, Value):
        pass

    def get_manufacturer(self):
        pass

    def get_board(self):
        pass

    def get_version_hardware(self):
        pass

    def get_version_firmware(self):
        pass

    def get_id(self):
        pass

    def set_led(self, value):
        pass

    def get_voltage_3v3(self):
        pass

    def get_voltage_5v(self):
        pass

    def get_voltage_9v(self):
        pass

    def get_voltage_battery(self):
        pass

    def set_sensor_type(self, port, type, params=0):
        i, _ = self._convert_port(port)
        self.SensorType[i] = type

    def transact_i2c(self, port, Address, OutArray, InBytes):
        pass

    def set_sensor(self, port, value):
        """A special method only available to dummy.BrickPi3.
        Used to change the internal value of the fake sensors."""
        i, _ = self._convert_port(port)
        sensorType = self.SensorType[i]
        self._internal_data[sensorType] = value

    def get_sensor(self, port):
        i, _ = self._convert_port(port)
        sensorType = self.SensorType[i]

        return self._internal_data[sensorType]

    def set_motor_power(self, port, power):
        i, _ = self._convert_port(port)
        self.Motors[i].set_power(power)

    def set_motor_position(self, port, position):
        i, _ = self._convert_port(port)
        self.Motors[i].go_position(position)

    def set_motor_position_relative(self, port, degrees):
        pos = self.get_motor_encoder(port)
        self.set_motor_position(port, pos + degrees)

    def set_motor_position_kp(self, port, kp=25):
        pass

    def set_motor_position_kd(self, port, kd=70):
        pass

    def set_motor_dps(self, port, dps):
        i, _ = self._convert_port(port)
        self.Motors[i].set_speed(dps)

    def set_motor_limits(self, port, power=0, dps=0):
        i, _ = self._convert_port(port)
        self.Motors[i].set_limits(power, dps)

    def get_motor_status(self, port):
        i, _ = self._convert_port(port)
        return [0, self.Motors[i].power, self.Motors[i].position, self.Motors[i].speed]

    def get_motor_encoder(self, port):
        i, _ = self._convert_port(port)
        return self.Motors[i].position

    def offset_motor_encoder(self, port, position):
        i, _ = self._convert_port(port)
        self.Motors[i].set_position(position)

    def reset_motor_encoder(self, port):
        i, _ = self._convert_port(port)
        self.Motors[i].set_position(0)

    def reset_all(self):
        pass


class Brick(BrickPi3):
    """
    Wrapper class for the BrickPi3 class. Comes with additional methods such get_sensor_status.
    """

    def __init__(self):
        pass

    def get_sensor_status(self, port: Literal[1, 2, 4, 8]):
        if port not in self.SensorType:
            return 5  # INCORRECT_SENSOR_PORT
        if self.SensorType[port] is None:
            return 1  # NOT_CONFIGURED
        return 0  # VALID_DATA
