from queue import Queue
from ..filters import JudiFilter
from serial import SerialException
from serial.tools.list_ports_common import ListPortInfo
from ..drivers import DummySerial, RemoteSerial, LocalSerial
import logging
from qtstrap import *
import time


class Signals(QObject):
    data_received = Signal(str)  # pre filter
    char_accepted = Signal(str)  # passes filter
    char_rejected = Signal(str)  # fails filter
    msg_completed = Signal(str)  # complete message


class SerialDeviceBase:
    log: logging.Logger | None = None

    def __init__(self, port=None, baud=9600):
        if self.log is None:
            self.log = logging.getLogger(__name__)

        self.base_signals = Signals()

        self.queue = Queue()
        self.filter = JudiFilter(self.base_signals.char_accepted.emit, self.base_signals.char_rejected.emit)
        self.active = False

        self.last_transmit_time = time.time()
        self.transmit_rate_limit = 0.01

        self.ser = None
        self.baud = baud

        if isinstance(port, ListPortInfo):
            self.port = port.device
        else:
            self.port = port

        if self.port:
            self.open()

    def set_baud_rate(self, baud):
        self.log.debug(f'{self.port}: setting baud to: {baud}')
        result = self.ser.set_baudrate(baud)

        if result:
            self.baud = baud
        else:
            self.log.debug(f'{self.port}: setting baud failed! {self.ser.error()}')

        return True

    def connect_socket(self, socket):
        socket.textMessageReceived.connect(self.send)

        def send_text_message(s):
            try:
                socket.sendTextMessage(s)
            except ValueError:
                self.log.exception(f'{self.port}')

        self.base_signals.data_received.connect(lambda s: send_text_message(s))

    def connect_stream(self, stream, stream_type='completed'):
        """
        connect a stream monitor to this SerialDevice
        types: raw, accepted, rejected, completed
        """
        stream.tx.connect(self.send)
        types = {
            'raw': self.base_signals.data_received,
            'accepted': self.base_signals.char_accepted,
            'rejected': self.base_signals.char_rejected,
            'completed': self.base_signals.msg_completed,
        }
        if stream_type in types:
            types[stream_type].connect(stream.rx)

    def open(self):
        """
        Open the serial port and set the device to active.

        Some port names trigger special behavior.
        """
        if self.port == 'DummyPort':
            self.ser = DummySerial()
            self.active = True
            return

        if self.port.startswith('RemoteSerial'):
            self.port = 'ws://' + self.port[len('RemoteSerial:') :]
            self.ser = RemoteSerial(port=self.port)
            self.active = True
            return

        try:
            self.ser = LocalSerial(port=self.port, baudrate=self.baud)
            self.active = True
        except PermissionError:
            # TODO: bad exception handling, it's not always a permission error
            self.log.exception(f'failed to open serial port on {self.port}')

    def close(self):
        """close the serial port and set the device to inactive"""
        if not self.active:
            return

        self.filter.reset()
        self.ser.close()
        self.active = False

    def send(self, string):
        """add a string to the outbound queue"""
        if not self.active:
            return

        self.log.debug(f'TX [{self.port}@{self.baud}]: {string}')
        self.queue.put(string)

    def transmit_next_message(self):
        """
        Pull a message from the outbound queue and transmit it to the serial port.

        This operation is rate limited by self.transmit_rate_limit.
        """
        if self.queue.empty():
            return

        if time_since(self.last_transmit_time) > self.transmit_rate_limit:
            try:
                self.ser.write(self.queue.get().encode())
                self.last_transmit_time = time.time()
            except SerialException:
                self.log.exception('serial write failed')

    def receive(self, string):
        """do something when a complete string is captured in self.communicate()"""
        self.log.debug(f'RX [{self.port}@{self.baud}]: {string}')
        self.base_signals.msg_completed.emit(string)

    def check_incoming_data(self):
        try:
            if self.ser.in_waiting:
                # grab everything
                data = self.ser.read(self.ser.in_waiting).decode(errors='ignore')
                # send the raw data signal
                self.base_signals.data_received.emit(data)
                # feed the data into the filter, one char at a time
                for c in data:
                    if self.filter.insert_char(c):
                        self.receive(self.filter.buffer)
                        self.filter.reset()

        except Exception as e:
            name = ''
            if hasattr(self, 'profile_name'):
                name = self.profile_name

            self.log.exception(f'{name}: {self.port} | {e}')

    def communicate(self):
        """Handle comms with the serial port. Call this often, from an event loop or something."""
        if not self.active:
            return

        self.transmit_next_message()
        self.check_incoming_data()
