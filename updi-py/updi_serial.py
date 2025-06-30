from time import sleep
import serial

class UpdiSerial:
    """
    Allows for serial communication with UPDI
    """

    def __init__(self, port, debug=False):
        self.port = port
        self.ser = serial.Serial(self.port, 57600, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_TWO, timeout=1.0)
        self.debug = debug

    def send(self, data):
        data_hex = ", ".join(list(map(hex, data)))
        self.dbg_print("SEND: {}".format(data_hex))
        
        self.ser.write(data)
    
        # handle echo
        self.ser.read(len(data))
    
    def receive(self, n):
        retries = 5

        while retries > 0:
            rec_val = self.ser.read(n)

            if len(rec_val) == n:
                break
            else:
                self.dbg_print("Retrying...")
                retries -= 1

        data_hex = ", ".join(list(map(hex, rec_val)))
        self.dbg_print("RECEIVE: {}".format(data_hex))

        return rec_val

    def send_double_break(self):
        self.dbg_print("Sending double break...")

        # for resetting, pulls the line low
        self.ser.close()

        tmp_ser = serial.Serial(self.port, 300, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE, timeout=1.0)

        tmp_ser.write([0x00])
        tmp_ser.read(1) # handle echo

        sleep(0.1)

        tmp_ser.write([0x00])
        tmp_ser.read(1) # handle echo

        tmp_ser.close()

        self.ser = serial.Serial(self.port, 57600, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_TWO, timeout=1.0)

    def dbg_print(self, s):
        if self.debug:
            print("\t\t\tUpdiSerial: {}".format(str(s)))
