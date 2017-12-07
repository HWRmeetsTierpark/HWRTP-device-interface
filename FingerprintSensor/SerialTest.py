import serial
import time

class FingerPrintCommunication(object):
    def __init__(self):
        self.uart = 0
        self.HEADER = 0xEF01
        self.PID_CMD = 0x01
        self.PID_DATA = 0x02
        self.PID_ACK = 0x07
        self.PID_EOD = 0x08

    def handShake(self):
        command = 0
        command += self.HEADER << (11 * 8)
        command += 0xFFFFFFFF << (7 * 8)
        command += self.PID_CMD << (6 * 8)
        command += 0x04 << (4 * 8)         # package length
        command += 0x17 << (3 * 8)         # instruction code
        command += 0x00 << (2 * 8)         # control code
        command += 0x1C                    # checksum
        print(hex(command))
        self.uart.write(hex(command).encode())
        ack = self.uart.read()
        print(ack)
        
    def readSysPar(self):
        command = 0
        command += self.HEADER << (10 * 8)
        command += 0xFFFFFFFF << (6 * 8)
        command += self.PID_CMD << (5 * 8)
        command += 0x03 << (3 * 8)         # package length
        command += 0x0F << (2 * 8)         # instruction code
        command += 0x13                    # checksum
        print(hex(command).encode())
        self.uart.write(hex(command).encode())
        time.sleep(1)
        while True:
            ack = self.uart.read()                
            print(ack)
        
    def init(self):
        self.uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=3.0)
        if self.uart.isOpen():
            self.uart.close()
        self.uart.open()
        time.sleep(1)
        #self.handShake()
        self.readSysPar()

if __name__ == "__main__":
    fingerPrintCom = FingerPrintCommunication()
    fingerPrintCom.init()
    
