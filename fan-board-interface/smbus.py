from i2c_aardvark import *
from util import *

def smbus_write(addr, reg, data=[], n_bytes=-1):
    if not isinstance(data, list):
        assert(n_bytes > 0)
        data = split_as_bytes(data, n_bytes)
        
    data.insert(0, reg)
    i2c_write(addr, data)
 
def smbus_read(addr, reg, n_bytes=1):
    i2c_write(addr, [reg], flags=AA_I2C_NO_STOP)
    return i2c_read(addr, n_bytes)
