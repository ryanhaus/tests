from time import sleep
from updi_constants import *

class UpdiNvm:
    def __init__(self, interface, debug=False):
        self.interface = interface
        self.debug = debug

    def store_reg(self, register, val):
        self.dbg_print(f"Writing {val:02X} to {register:X}")

        self.interface.sts(
            SIZE_WORD,
            SIZE_BYTE,
            NVMCTRL_ADDR_BASE + register,
            val
        )

    def load_reg(self, register):
        val = self.interface.lds(
            SIZE_WORD,
            SIZE_BYTE,
            NVMCTRL_ADDR_BASE + register
        )

        self.dbg_print(f"NVM Register {register:X} = {val:02X}")

        return val

    def wait_ready(self):
        self.dbg_print("Waiting for NVM...")
        while self.load_reg(NVM_REG_STATUS) & (1 << 0) > 0:
            sleep(0.01)

    def exec_cmd(self, cmd):
        self.dbg_print(f"Executing command {cmd:X}")

        self.store_reg(NVM_REG_CTRLA, cmd)

    def dbg_print(self, s):
        if self.debug:
            print("\tUpdiNvm: {}".format(str(s)))
