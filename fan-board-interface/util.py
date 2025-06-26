# Utility functions
def join_as_val(arr):
    x = 0
    
    for (i, val) in enumerate(arr):
        x |= val << (8 * i)
        
    return x
    
def join_as_string(arr):
    return bytes(reversed(arr)).decode("utf-8")
    
def split_as_bytes(val, n):
    x = []
    
    for i in range(n):
        x.append(val & 0xFF)
        val >>= 8
    
    return x
