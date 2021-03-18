from .serial_device import SerialDevice
from .remote_serial import RemoteSerial

from .judi_filter import JudiFilter
from .null_filter import NullFilter
from .newline_filter import NewlineFilter
from .delimiter_filter import DelimiterFilter

from .judi_mixin import JudiStandardMixin
from .judi_responder import JudiResponder

from .console_device import ConsoleDevice
from .unknown_device import UnknownDevice, DeviceStates

try:
    from plugins.devices import *
except:
    pass

profiles = {p.profile_name: p for p in SerialDevice.__subclasses__()}

profile_names = sorted(profiles.keys())

from .device_manager import DeviceManager
from .subscriptions import SubscriptionManager
from .device_controls import DeviceControlsWidget, DeviceControlsDockWidget