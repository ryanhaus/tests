from updi_serial import UpdiSerial
from updi_constants import *

class UpdiInterface:
    """
    Provides an interface to send UPDI instructions
    using serial. See datasheet section 33.3 for more
    information.
    """

    def __init__(self, serial, debug=False):
        self.serial = serial
        self.debug = debug

    # load from data space using direct addressing
    def lds(self, size_a, size_b, addr):
        self.dbg_print(f"LDS, size_a={size_a}, size_b={size_b}, addr={addr}")

        # write command and address
        if size_a == SIZE_BYTE:
            # byte address
            self.serial.send([
                SYNCH,
                OPCODE_LDS | ((size_a & 0b11) << 2) | (size_b & 0b11),
                addr & 0xFF
            ])

        elif size_a == SIZE_WORD:
            # word address (little-endian)
            self.serial.send([
                SYNCH,
                OPCODE_LDS | ((size_a & 0b11) << 2) | (size_b & 0b11),
                addr & 0xFF,
                (addr >> 8) & 0xFF
            ])

        # read result
        if size_b == SIZE_BYTE:
            return self.serial.receive(1)[0]

        elif size_b == SIZE_WORD:
            return self.serial.receive(2)

    # store to data space using direct addressing
    def sts(self, size_a, size_b, addr, data):
        self.dbg_print(f"STS, size_a={size_a}, size_b={size_b}, addr={addr}, data={data}")

        # write address
        if size_a == SIZE_BYTE:
            self.serial.send([
                SYNCH,
                OPCODE_STS | ((size_a & 0b11) << 2) | (size_b & 0b11),
                addr & 0xFF
            ])

        elif size_a == SIZE_WORD:
            self.serial.send([
                SYNCH,
                OPCODE_STS | ((size_a & 0b11) << 2) | (size_b & 0b11),
                addr & 0xFF,
                (addr >> 8) & 0xFF
            ])

        assert self.serial.receive(1)[0] == ACK

        # write data
        if size_b == SIZE_BYTE:
            self.serial.send([ data & 0xFF ])

        elif size_b == SIZE_WORD:
            self.serial.send([
                data & 0xFF,
                (data >> 8) & 0xFF
            ])

        assert self.serial.receive(1)[0] == ACK

    # load from data space using indirect addressing
    def ld(self, ptr, size_ab, n=1):
        self.dbg_print(f"LD, ptr={ptr}, size_ab={size_ab}, n={n}")

        self.serial.send([
            SYNCH,
            OPCODE_LD | ((ptr & 0b11) << 2) | (size_ab & 0b11)
        ])

        if size_ab == SIZE_BYTE:
            if n == 1:
                return self.serial.receive(1)[0]
            else:
                return self.serial.receive(n)

        elif size_ab == SIZE_WORD:
            return self.serial.receive(2 * n)
        
    # store to data space using indirect addressing (or to set the pointer)
    def st(self, ptr, size_ab, addr_data, check_ack=True):
        self.dbg_print(f"ST, ptr={ptr}, size_ab={size_ab}, addr_data={addr_data}")

        if size_ab == SIZE_BYTE:
            self.serial.send([
                SYNCH,
                OPCODE_ST | ((ptr & 0b11) << 2) | (size_ab & 0b11),
                addr_data & 0xFF
            ])

        elif size_ab == SIZE_WORD:
            self.serial.send([
                SYNCH,
                OPCODE_ST | ((ptr & 0b11) << 2) | (size_ab & 0b11),
                addr_data & 0xFF,
                (addr_data >> 8) & 0xFF
            ])

        if check_ack:
            assert self.serial.receive(1)[0] == ACK

    # load from control/status space
    def ldcs(self, cs_addr):
        self.dbg_print(f"LDCS, cs_addr={cs_addr}")

        # write address
        self.serial.send([
            SYNCH,
            OPCODE_LDCS | (cs_addr & 0xF)
        ])

        # read response
        return self.serial.receive(1)[0]

    # store to control/status space
    def stcs(self, cs_addr, data):
        self.dbg_print(f"STCS, cs_addr={cs_addr}, data={data}")

        self.serial.send([
            SYNCH,
            OPCODE_STCS | (cs_addr & 0xF),
            data & 0xFF
        ])

    # set repeat counter (note that rpt_0 + 1 repeats will occur)
    def repeat(self, rpt_0):
        self.dbg_print(f"REPEAT, rpt_0={rpt_0}")

        self.serial.send([
            SYNCH,
            OPCODE_REPEAT,
            rpt_0 & 0xFF
        ])

    # set activation key, or read system info block (SIB)
    def key(self, sib=0, size_c=None, key=None):
        self.dbg_print("KEY, sib={}, size_c={}, key=[{}]".format(sib, size_c if size_c else "None", ", ".join([hex(x) for x in key]) if key else "None"))

        if sib == 1:
            self.serial.send([
                SYNCH,
                OPCODE_KEY | 0b100 | size_c
            ])

            return self.serial.receive(8 if size_c == KEY_SIZE_8 else 16)
        else:
            # send key
            self.serial.send([
                SYNCH,
                OPCODE_KEY
            ])

            assert len(key) == 8

            self.serial.send(key)
    
    def dbg_print(self, s):
        if self.debug:
            print("\t\tUpdiInterface: {}".format(str(s)))
