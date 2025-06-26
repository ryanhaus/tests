# Utility functions

# Joins an array of 8-bit values into an integer value, with the first entry in
# the array being the LSB.
def join_as_val(arr):
    x = 0
    
    for (i, val) in enumerate(arr):
        x |= (val & 0xFF) << (8 * i)
        
    return x
    
# Joins an array of 8-bit values into a string, with the first entry being the
# last character.
def join_as_string(arr):
    return bytes(reversed(arr)).decode("utf-8")
    
# Splits an integer value into n 8-bit bytes, with the first entry in the
# output array being the LSB.
def split_as_bytes(val, n):
    x = []
    
    for i in range(n):
        x.append(val & 0xFF)
        val >>= 8
    
    return x
