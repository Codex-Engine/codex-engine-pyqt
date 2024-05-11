from qtpy.QtSerialPort import QSerialPort
from serial import Serial


class LocalSerial2:
    def __init__(self, *args, **kwargs):
        self.ser = Serial(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.ser, name)
    

class LocalSerial:
    def __init__(self, port='', baudrate=9600):
        self.ser = QSerialPort()
        self.ser.setPortName(port)
        self.ser.setBaudRate(baudrate)

        self.open()

    def open(self) -> bool:
        return self.ser.open(QSerialPort.ReadWrite)

    def close(self):
        self.ser.close()

    def write(self, string):
        self.ser.write(string)

    def read(self, number=1):
        return bytes(self.ser.read(number))

    def set_baudrate(self, baudrate):
        return self.ser.setBaudRate(baudrate)

    @property
    def in_waiting(self):
        return self.ser.bytesAvailable()
