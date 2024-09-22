from serial import Serial


class LocalSerial:
    def __init__(self, port='', baudrate=9600):
        self.ser = Serial(port=port, baudrate=baudrate)

    def open(self) -> bool:
        self.ser.open()
        return True

    def close(self):
        self.ser.close()

    def write(self, string):
        self.ser.write(string)

    def read(self, number=1):
        return bytes(self.ser.read(number))

    def error(self):
        return None

    def set_baudrate(self, baudrate):
        self.ser.baudrate = baudrate
        return True

    @property
    def in_waiting(self):
        return self.ser.in_waiting
