from i2c_aardvark import *
from util import *

# Writes a value to a register using SMBus.
def smbus_write(addr, reg, data=[], n_bytes=-1):
    if not isinstance(data, list):
        assert(n_bytes > 0)
        data = split_as_bytes(data, n_bytes)
        
    data.insert(0, reg)
    i2c_write(addr, data)
 
# Reads a value from a register using SMBus.
def smbus_read(addr, reg, n_bytes=1):
    i2c_write(addr, [reg], nostop=True)
    return i2c_read(addr, n_bytes)
