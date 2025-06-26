# AT24C128 EEPROM
from i2c_aardvark import *
from util import *
from time import sleep

EEPROM_ADDR = 0x54
T_WR = 0.01 # EEPROM write time

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

def eeprom_read_random(addr, n):
    addr_low = addr & 0xFF
    addr_high = (addr & 0xFF00) >> 8

    i2c_write(EEPROM_ADDR, [addr_high, addr_low], flags=AA_I2C_NO_STOP)
    return i2c_read(EEPROM_ADDR, n)

def eeprom_read_cur(n):
    return i2c_read(EEPROM_ADDR, n)
