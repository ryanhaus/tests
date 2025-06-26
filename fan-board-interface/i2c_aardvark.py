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
 
def i2c_write(addr, data, flags=AA_I2C_NO_FLAGS):
    aa_i2c_write(handle, addr, flags, array('B', data))
 
def i2c_read(addr, n_bytes, flags=AA_I2C_NO_FLAGS):
    (_count, data) = aa_i2c_read(handle, addr, flags, n_bytes)
    data = list(data)
    
    return data
