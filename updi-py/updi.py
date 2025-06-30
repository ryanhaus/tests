import serial
from time import sleep

from updi_serial import UpdiSerial
from updi_interface import UpdiInterface
from updi_nvm import UpdiNvm
from updi_programmer import UpdiProgrammer
from updi_rom import UpdiRom
from updi_constants import *

def main():
    DEBUG = True
    updi_serial = UpdiSerial("/dev/ttyUSB0", debug=DEBUG)
    updi_interface = UpdiInterface(updi_serial, debug=DEBUG)
    updi_nvm = UpdiNvm(updi_interface, debug=DEBUG)
    updi_programmer = UpdiProgrammer(updi_interface, updi_nvm, debug=DEBUG)
    updi_rom = UpdiRom("rom.hex", debug=DEBUG)

    # reset UPDI
    print("Resetting UPDI...")
    updi_serial.send_double_break()

    # get status
    status = updi_interface.ldcs(REG_STATUSA)

    if status == 0:
        print("Error: UPDI status is 0")
        return
    print(f"UPDI Status: 0x{status:02X}")

    response = updi_interface.key(1, 0b01)
    print("SIB: {}".format(response.decode("utf8")))

    print("Erasing/unlocking chip...")
    updi_programmer.unlock_chiperase()

    print("Enabling NVM programming mode for full chip access...")
    updi_programmer.unlock_nvmprog()

    device_id = updi_programmer.read_bytes(SIGNATURES_ADDR_BASE, 3)
    #print(", ".join([hex(x) for x in device_id]))
    device_id = ''.join([hex(x).upper()[2:] for x in device_id])
    print(f"Device ID: {device_id}")

    print("Programming ROM...")
    updi_programmer.program_rom(updi_rom)

    print("Verifying ROM...")
    updi_programmer.verify_rom(updi_rom)
    
    print("Resetting...")
    updi_programmer.reset_device()

    print("Done")

if __name__ == "__main__":
    main()
