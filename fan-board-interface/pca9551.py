# PCA9551 LED controller
from smbus import *

LEDCTRL_ADDR = 0x60
LEDCTRL_INPUT = 0x00
LEDCTRL_PSC0 = 0x01
LEDCTRL_PWM0 = 0x02
LEDCTRL_PSC1 = 0x03
LEDCTRL_PWM1 = 0x04
LEDCTRL_LS0 = 0x05
LEDCTRL_LS1 = 0x06

def ledctrl_write(reg, data):
    smbus_write(LEDCTRL_ADDR, reg, [data])
    
def ledctrl_read(reg):
    return smbus_read(LEDCTRL_ADDR, reg, 1)
