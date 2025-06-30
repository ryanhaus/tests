from time import sleep
from updi_constants import *

class UpdiProgrammer:
    def __init__(self, interface, nvm, debug=False):
        self.interface = interface
        self.nvm = nvm
        self.debug = debug

    def unlock_chiperase(self):
        self.dbg_print("Sending CHIPERASE key...")
        self.interface.key(key=KEY_CHIPERASE)

        self.dbg_print("Verifying CHIPERASE status...")
        asi_key_status = self.interface.ldcs(REG_ASI_KEY_STATUS)
        #self.dbg_print(hex(asi_key_status))
        assert (asi_key_status & (1 << 3)) > 0

        self.reset_device()

        self.dbg_print("Awaiting Chip Erase Finish...")
        while self.interface.ldcs(REG_ASI_SYS_STATUS) & (1 << 0) > 0:
            sleep(0.01)

        self.dbg_print("Chip erase finished.")

    def unlock_nvmprog(self):
        self.dbg_print("Sending NVMPROG key...")
        self.interface.key(key=KEY_NVMPROG)

        self.dbg_print("Verifying NVMPROG status...")
        asi_key_status = self.interface.ldcs(REG_ASI_KEY_STATUS)
        #self.dbg_print(hex(asi_key_status))
        assert (asi_key_status & (1 << 4)) > 0

        self.reset_device()

        self.dbg_print("Awaiting NVM Programming Mode activation...")
        while self.interface.ldcs(REG_ASI_SYS_STATUS) & (1 << 3) == 0:
            sleep(0.01)

        self.dbg_print("NVM Programming Mode activated.")

    def reset_device(self):
        self.dbg_print("Issuing System Reset...")
        self.interface.stcs(REG_ASI_RESET_REQ, RESET_SIGNATURE)

        sleep(0.1)

        self.dbg_print("Clearing System Reset...")
        self.interface.stcs(REG_ASI_RESET_REQ, 0x00)

    def read_bytes(self, addr, n):
        self.interface.st(PTR_VAL, SIZE_WORD, addr & 0xFFFF)

        if n > 1:
            self.interface.repeat(n - 1) # n-1 repeats = n bytes read

        return self.interface.ld(PTR_DEREF_INC, SIZE_BYTE, n)

    def write_bytes(self, addr, data, words=True):
        self.dbg_print("Writing bytes: [{}]".format(", ".join(map(hex, data))))

        # clear page buffer
        self.nvm.wait_ready()
        self.nvm.exec_cmd(NVM_OPCODE_PBC)

        # write to page buffer
        self.nvm.wait_ready()

        self.dbg_print("Writing...")
        self.interface.st(PTR_VAL, SIZE_WORD, addr & 0xFFFF)

        if words:
            # write using words
            if len(data) > 2:
                self.interface.repeat((len(data) >> 1) - 1) # (n/2)-1 repeats = n bytes written
            
            word = ((data[0] or 0) & 0xFF) | (((data[1] or 0) & 0xFF) << 8)
            self.interface.st(PTR_DEREF_INC, SIZE_WORD, word)

            for i in range(2, len(data)-1, 2):
                self.interface.serial.send([data[i] or 0, data[i+1] or 0])
                assert self.interface.serial.receive(1)[0] == ACK
        else:
            # write each individual byte
            if len(data) > 1:
                self.interface.repeat(len(data) - 1) # n-1 repeats = n bytes written

            self.interface.st(PTR_DEREF_INC, SIZE_BYTE, data[0])

            for x in data[1:]:
                self.interface.serial.send([x])
                assert self.interface.serial.receive(1)[0] == ACK

        # write the page buffer
        self.nvm.exec_cmd(NVM_OPCODE_WP)
        self.nvm.wait_ready()


    def program_rom(self, rom):
        self.dbg_print("Programming ROM...")

        for segment in rom.rom.segments():
            start,end = segment
            self.dbg_print(f"Writing segment from {start:X} to {end:X}...")

            data = []
            for addr in range(start, end):
                data.append(rom.rom[addr])

            for i in range(0, len(data), 0x40):
                block_end = min(i+0x40, len(data))
                self.dbg_print(f"Writing block from {i:X} to {block_end:X}")

                self.write_bytes(FLASH_ADDR_BASE + start + i, data[i:block_end])

    def verify_rom(self, rom):
        self.dbg_print("Verifying ROM...")

        for segment in rom.rom.segments():
            start,end = segment
            self.dbg_print(f"Reading segment from {start:X} to {end:X}...")

            # read from supplied ROM
            data = []
            for addr in range(start, end):
                data.append(rom.rom[addr])

            # read from flash
            flash = []
            for i in range(0, len(data), 0x40):
                block_end = min(i+0x40, len(data))
                block_len = block_end - i

                self.dbg_print(f"Reading block from {i:X} to {block_end:X}")

                flash += self.read_bytes(FLASH_ADDR_BASE + start + i, block_len)
            
            # verify
            verified = data == flash

            self.dbg_print(f"Verification result: {verified}")

            return verified

    def dbg_print(self, s):
        if self.debug:
            print("\tUpdiProgrammer: {}".format(str(s)))
