from queue import Queue
from .judi_filter import JudiFilter
from serial import Serial, SerialException
from serial.tools.list_ports_common import ListPortInfo
from .dummy_serial import DummySerial
from .remote_serial import RemoteSerial
import logging
from qt import *
import time


class Signals(QObject):
    send = Signal(str)
    rejected = Signal(str)


class SerialDeviceBase:
    log = None

    def __init__(self, port=None, baud=9600):
        if self.log == None:
            self.log = logging.getLogger(__name__)
            
        self.base_signals = Signals()

        self.queue = Queue()
        self.filter = JudiFilter(self.base_signals.rejected.emit)
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

    def connect_socket(self, socket):
        socket.textMessageReceived.connect(self.send)

        def send_text_message(s):
            try:
                socket.sendTextMessage(s)
            except ValueError as e:
                self.log.exception(f'{self.port}')
            
        self.base_signals.send.connect(lambda s: send_text_message(s))

    def set_baud_rate(self, baud):
        try:
            self.ser.baudrate = baud
            self.baud = baud
        except:
            return False
        return True

    def connect_monitor(self, monitor):
        monitor.tx.connect(self.send)
        self.base_signals.send.connect(monitor.rx)
        self.base_signals.rejected.connect(monitor.rx)

    def connect_serial_port_monitor(self, monitor):
        monitor.tx.connect(self.send)
        self.base_signals.rejected.connect(monitor.rx)

    def open(self):
        """ open the serial port and set the device to active """
        if self.port == "DummyPort":
            self.ser = DummySerial()
            self.active = True
            return

        if self.port.startswith("RemoteSerial"):
            self.port = 'ws://' + self.port[len("RemoteSerial:"):]
            self.ser = RemoteSerial(port=self.port)
            self.active = True
            return

        try:
            self.ser = Serial(port=self.port, baudrate=self.baud, timeout=0, write_timeout=0)
            self.active = True
        except Exception as e:
            # TODO: bad exception handling, it's not always a permission error
            self.log.exception("PermissionError" + str(e))

    def close(self):
        """ close the serial port and set the device to inactive """
        if not self.active:
            return

        self.filter.reset()
        self.ser.close()
        self.active = False

    def send(self, string):
        """ add a string to the outbound queue """
        if not self.active:
            return

        self.log.debug(f"TX: {string}")

        self.queue.put(string)

    def recieve(self, string):
        """ do something when a complete string is captured in self.communicate() """
        self.log.debug(f"RX: {string}")
        
        self.base_signals.send.emit(string)

    def message_completed(self):
        msg = self.filter.buffer
        self.base_signals.send.emit(msg)
        self.recieve(msg)
        self.filter.reset()

    def transmit_next_message(self):
        sent = False
        if not self.queue.empty():
            if time_since(self.last_transmit_time) > self.transmit_rate_limit:
                try:
                    self.ser.write(self.queue.get().encode())
                    sent = True
                except SerialException as e:
                    self.log.exception(e)
                self.last_transmit_time = time.time()
        return sent

    def communicate(self):
        """ Handle comms with the serial port. Call this often, from an event loop or something. """
        if not self.active:
            return

        self.transmit_next_message()

        # serial recieve
        try:
            while self.ser.in_waiting:
                if self.filter.insert_char(self.ser.read(1).decode(errors='ignore')):
                    break
        except Exception as e:
            name = ''
            if hasattr(self, 'profile_name'):
                name = self.profile_name
                
            self.log.exception(f"{name}: {self.port} | {e}")

        # handle completed message
        if self.filter.completed():
            self.message_completed()