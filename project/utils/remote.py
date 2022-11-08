from typing import Literal
from . import brick
from . import dummy
from .rmi import RemoteClient, RemoteServer, isrelatedclass


class RemoteBrickClient(RemoteClient):
    def __init__(self, address, password, port=None, sock=None):
        super(RemoteBrickClient, self).__init__(address, password, port, sock)
        self._brick: dummy.Brick = self.create_caller(
            dummy.Brick(), var_name='brick')

    def get_brick(self):
        return self._brick

    def make_remote(self, sensor_or_motor, *args, **kwargs):
        """Creates a remote sensor or motor that is attached to the remote brick.
        sensor_or_motor - A class, such as Motor or EV3UltrasonicSensor
        *args - any of the normal arguments that would be used to create the object locally

        Returns None if you gave the wrong class.
        """
        if isrelatedclass(sensor_or_motor, (brick.Motor, brick.Sensor)):
            kwargs.update({'bp': self._brick})
            return sensor_or_motor(*args, **kwargs)
        return None

    def set_default_brick(self):
        """Sets this RemoteBrickClient to be the default brick for all newly initialized motors or sensors.
        Use brick.restore_default_brick() to reset back to normal.

        This will only apply to newly created devices.

        Normal defined as:
        - The useless dummy brick on PCs
        - The actual BrickPi itself, if running this code on the BrickPi
        """
        brick.BP = self._brick


class RemoteBrickServer(RemoteServer):
    def __init__(self, password, port=None):
        super(RemoteBrickServer, self).__init__(password, port)
        self.register_object(brick.BP, var_name='brick')


class RemoteEV3UltrasonicSensor(brick.EV3UltrasonicSensor):
    def __init__(self, client: RemoteBrickClient, port: Literal[1, 2, 3, 4], mode="cm"):
        super(RemoteEV3UltrasonicSensor, self).__init__(
            port, mode=mode, bp=client.get_brick())


class RemoteEV3ColorSensor(brick.EV3ColorSensor):
    def __init__(self, client: RemoteBrickClient, port: Literal[1, 2, 3, 4], mode="component"):
        super(RemoteEV3ColorSensor, self).__init__(
            port, mode=mode, bp=client.get_brick())


class RemoteEV3GyroSensor(brick.EV3GyroSensor):
    def __init__(self, client: RemoteBrickClient, port: Literal[1, 2, 3, 4], mode="both"):
        super(RemoteEV3GyroSensor, self).__init__(
            port, mode=mode, bp=client.get_brick())


class RemoteTouchSensor(brick.TouchSensor):
    def __init__(self, client: RemoteBrickClient, port: Literal[1, 2, 3, 4], mode: str = "touch"):
        super(RemoteTouchSensor, self).__init__(
            port, mode=mode, bp=client.get_brick())


class RemoteMotor(brick.Motor):
    def __init__(self, client: RemoteBrickClient, port: Literal["A", "B", "C", "D"]):
        super(RemoteMotor, self).__init__(port, bp=client.get_brick())
