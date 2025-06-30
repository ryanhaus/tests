from intelhex import IntelHex

class UpdiRom:
    def __init__(self, rom_file_name, debug=False):
        self.rom = IntelHex()
        self.rom.loadhex(rom_file_name)

        self.debug = debug

        for segment in self.rom.segments():
            start,end = segment
            self.dbg_print("SEGMENT {}-{}:".format(hex(start), hex(end)))

            s = "\t"
            for address in range(start, end):
                s += "{} ".format(hex(self.rom[address]))

            self.dbg_print(s)

    def dbg_print(self, s):
        if self.debug:
            print("UpdiRom: {}".format(str(s)))
