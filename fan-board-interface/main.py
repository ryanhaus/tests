#!/usr/bin/env python3
from aardvark_py import *
 
# Aardvark abstraction
handle = aa_open(0)
 
def i2c_init():
    aa_configure(handle, AA_CONFIG_SPI_I2C)
    aa_i2c_pullup(handle, AA_I2C_PULLUP_BOTH)
    aa_i2c_bitrate(handle, 100)
    aa_i2c_bus_timeout(handle, 1000)
 
def i2c_deinit():
    aa_close(handle)
 
def i2c_write(addr, data):
    aa_i2c_write(handle, addr, AA_I2C_NO_FLAGS, array('B', data))
 
def i2c_read(addr, n):
    (_count, data) = aa_i2c_read(handle, addr, AA_I2C_NO_FLAGS, n)
    return data
# End Aardvark abstraction
 
# SMBus
# Requires I2C to be setup
def smbus_write(addr, reg, data):
    data.insert(0, reg)
    i2c_write(addr, data)
 
def smbus_read(addr, reg, n):
    i2c_write(addr, [reg])
    return i2c_read(addr, n)
# End SMBus
 
# EEPROM
# Requires I2C to be setup
def eeprom_write(i2c_addr, addr, data):
    assert(len(data) <= 64)

    addr_low = addr & 0xFF
    addr_high = (addr & 0xFF00) >> 8

    data.insert(0, addr_low)
    data.insert(0, addr_high)
    i2c_write(i2c_addr, data)

def eeprom_read_random(i2c_addr, addr, n):
    addr_low = addr & 0xFF
    addr_high = (addr & 0xFF00) >> 8

    i2c_write(i2c_addr, [addr_high, addr_low])
    return i2c_read(i2c_addr, n)

def eeprom_read_cur(i2c_addr, n):
    return i2c_read(i2c_addr, n)
# End EEPROM
 
def main():
    i2c_init()
 
    # LED Controller (PCA9551)
    LEDCTRL_ADDR = 0x60
    LEDCTRL_REG_INPUT = 0x00
    LEDCTRL_REG_PSC0 = 0x01
    LEDCTRL_REG_PWM0 = 0x02
    LEDCTRL_REG_PSC1 = 0x03
    LEDCTRL_REG_PWM1 = 0x04
    LEDCTRL_REG_LS0 = 0x05
    LEDCTRL_REG_LS1 = 0x06
    smbus_write(LEDCTRL_ADDR, LEDCTRL_REG_LS0, [0x0A])
    smbus_write(LEDCTRL_ADDR, LEDCTRL_REG_PSC0, [0x10])
 
    # EEPROM
    EEPROM_ADDR = 0x54
 
    # Fan Controller
    FAN_CONTROLLER_ADDR = 0x60
 
    i2c_deinit()
 
if __name__ == "__main__":
    main()
