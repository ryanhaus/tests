# AT24C128 EEPROM
from i2c_aardvark import *
from util import *
from time import sleep

EEPROM_ADDR = 0x54
T_WR = 0.01 # EEPROM write time

# Writes an arbitrarily long amount of data to the EEPROM. If 'data' is longer
# than 64 bytes, it will be written in pages of 64. 'data' can also be of type
# int, in which case the n_bytes parameter is also required.
def eeprom_write(addr, data=[], n_bytes=-1):
    if not isinstance(data, list):
        assert(n_bytes > 0)
        
        data = split_as_bytes(data, n_bytes)
        
    if len(data) > 64:
        eeprom_write(addr, data[0:64])
        eeprom_write(addr + 64, data[64:])
        return
    
    print(f"Writing to 0x{addr:04X}")

    addr_low = addr & 0xFF
    addr_high = (addr & 0xFF00) >> 8

    data.insert(0, addr_low)
    data.insert(0, addr_high)
    i2c_write(EEPROM_ADDR, data)
    
    sleep(T_WR)

# Reads n bytes from a given address.
def eeprom_read_random(addr, n):
    addr_low = addr & 0xFF
    addr_high = (addr & 0xFF00) >> 8

    i2c_write(EEPROM_ADDR, [addr_high, addr_low], nostop=True)
    return i2c_read(EEPROM_ADDR, n)

# Reads n bytes from the current address pointer.
def eeprom_read_cur(n):
    return i2c_read(EEPROM_ADDR, n)
