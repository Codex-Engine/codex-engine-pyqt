from qtpy.QtSerialPort import QSerialPort
import logging


class LocalSerial:
    def __init__(self, port='', baudrate=9600):
        self.log = logging.getLogger(__name__)

        self.ser = QSerialPort()
        self.ser.setPortName(port)
        self.ser.setBaudRate(baudrate)
        self.log.info(f'creating LocalSerial: {port}@{baudrate}')

        self.open()

    def open(self) -> bool:
        return self.ser.open(QSerialPort.ReadWrite)

    def close(self):
        self.ser.close()

    def write(self, string):
        self.ser.write(string)

    def read(self, number=1):
        return bytes(self.ser.read(number))

    @property
    def baudrate(self):
        return self.ser.baudRate()

    @baudrate.setter
    def set_baudrate(self, baudrate):
        self.log.info(f'setting baudrate {baudrate}')
        self.ser.setBaudRate(baudrate)

    @property
    def in_waiting(self):
        return self.ser.bytesAvailable()
