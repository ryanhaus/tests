# MAX31785 fan controller
from smbus import *
from util import *

FANCTRL_ADDR = 0x53

# COMMAND = (code, n bytes)
FANCTRL_PAGE =                      (0x00, 1)
FANCTRL_CLEAR_FAULTS =              (0x03, 0)
FANCTRL_WRITE_PROTECT =             (0x10, 1)
FANCTRL_STORE_DEFAULT_ALL =         (0x11, 0)
FANCTRL_RESTORE_DEFAULT_ALL =       (0x12, 0)
FANCTRL_CAPABILITY =                (0x19, 1)
FANCTRL_VOUT_MODE =                 (0x20, 1)
FANCTRL_VOUT_SCALE_MONITOR =        (0x2A, 2)
FANCTRL_FAN_CONFIG_1_2 =            (0x3A, 1)
FANCTRL_FAN_COMMAND_1 =             (0x3B, 2)
FANCTRL_VOUT_OV_FAULT_LIMIT =       (0x40, 2)
FANCTRL_VOUT_OV_WARN_LIMIT =        (0x42, 2)
FANCTRL_VOUT_UV_WARN_LIMIT =        (0x43, 2)
FANCTRL_VOUT_UV_FAULT_LIMIT =       (0x44, 2)
FANCTRL_OT_FAULT_LIMIT =            (0x4F, 2)
FANCTRL_OT_WARN_LIMIT =             (0x51, 2)
FANCTRL_STATUS_BYTE =               (0x78, 1)
FANCTRL_STATUS_WORD =               (0x79, 2)
FANCTRL_STATUS_VOUT =               (0x7A, 1)
FANCTRL_STATUS_CML =                (0x7E, 1)
FANCTRL_STATUS_MFR_SPECIFIC =       (0x80, 1)
FANCTRL_STATUS_FANS_1_2 =           (0x81, 1)
FANCTRL_READ_VOUT =                 (0x8B, 2)
FANCTRL_READ_TEMPERATURE_1 =        (0x8D, 2)
FANCTRL_READ_FAN_SPEED_1 =          (0x90, 2)
FANCTRL_PMBUS_REVISION =            (0x98, 1)
FANCTRL_MFR_ID =                    (0x99, 1)
FANCTRL_MFR_MODEL =                 (0x9A, 1)
FANCTRL_MFR_REVISION =              (0x9B, 2)
FANCTRL_MFR_LOCATION =              (0x9C, 8)
FANCTRL_MFR_DATE =                  (0x9D, 8)
FANCTRL_MFR_SERIAL =                (0x9E, 8)
FANCTRL_MFR_MODE =                  (0xD1, 2)
FANCTRL_MFR_VOUT_PEAK =             (0xD4, 2)
FANCTRL_MFR_TEMPERATURE_PEAK =      (0xD6, 2)
FANCTRL_MFR_VOUT_MIN =              (0xD7, 2)
FANCTRL_MFR_FAULT_RESPONSE =        (0xD9, 1)
FANCTRL_MFR_NV_FAULT_LOG =          (0xDC, 255)
FANCTRL_MFR_TIME_COUNT =            (0xDD, 4)
FANCTRL_MFR_TEMP_SENSOR_CONFIG =    (0xF0, 2)
FANCTRL_MFR_FAN_CONFIG =            (0xF1, 2)
FANCTRL_MFR_FAN_LUT =               (0xF2, 32)
FANCTRL_MFR_READ_FAN_PWM =          (0xF3, 2)
FANCTRL_MFR_FAN_FAULT_LIMIT =       (0xF5, 2)
FANCTRL_MFR_FAN_WARN_LIMIT =        (0xF6, 2)
FANCTRL_MFR_FAN_RUN_TIME =          (0xF7, 2)
FANCTRL_MFR_FAN_PWM_AVG =           (0xF8, 2)
FANCTRL_MFR_FAN_PWM2RPM =           (0xF9, 8)

# CODE: (readable pages, writeable pages)
FANCTRL_PAGES_0_5 = 0b0001
FANCTRL_PAGES_6_16 = 0b0010
FANCTRL_PAGES_17_22 = 0b0100
FANCTRL_PAGE_255 = 0b1000

FANCTRL_ACCESS = {
    0x00: (0b1111, 0b1111),
    0x03: (0b0000, 0b1111),
    0x10: (0b1111, 0b1111),
    0x11: (0b0000, 0b1111),
    0x12: (0b0000, 0b1111),
    0x19: (0b1111, 0b0000),
    0x20: (0b1111, 0b0000),
    0x2A: (0b0100, 0b0100),
    0x3A: (0b0001, 0b0001),
    0x3B: (0b0001, 0b0001),
    0x40: (0b0100, 0b0100),
    0x42: (0b0100, 0b0100),
    0x43: (0b0100, 0b0100),
    0x44: (0b0100, 0b0100),
    0x4F: (0b0010, 0b0010),
    0x51: (0b0010, 0b0010),
    0x78: (0b1111, 0b0000),
    0x79: (0b1111, 0b0000),
    0x7A: (0b0100, 0b0000),
    0x7E: (0b1111, 0b0000),
    0x80: (0b0010, 0b0000),
    0x81: (0b0001, 0b0000),
    0x8B: (0b0100, 0b0000),
    0x8D: (0b0010, 0b0000),
    0x90: (0b0001, 0b0000),
    0x98: (0b1111, 0b0000),
    0x99: (0b1111, 0b0000),
    0x9A: (0b1111, 0b0000),
    0x9B: (0b1111, 0b0000),
    0x9C: (0b1111, 0b1111),
    0x9D: (0b1111, 0b1111),
    0x9E: (0b1111, 0b1111),
    0xD1: (0b1111, 0b1111),
    0xD4: (0b0100, 0b0100),
    0xD6: (0b0010, 0b0010),
    0xD7: (0b0100, 0b0100),
    0xD9: (0b0111, 0b0111),
    0xDC: (0b1111, 0b0000),
    0xDD: (0b1111, 0b1111),
    0xF0: (0b0010, 0b0010),
    0xF1: (0b0001, 0b0001),
    0xF2: (0b0001, 0b0001),
    0xF3: (0b0001, 0b0000),
    0xF5: (0b0001, 0b0001),
    0xF6: (0b0001, 0b0001),
    0xF7: (0b0001, 0b0001),
    0xF8: (0b0001, 0b0001),
    0xF9: (0b0001, 0b0001),
}



current_page = 0
def assert_page_ok(reg, write=False, read=False):
    (readable_pages, writeable_pages) = FANCTRL_ACCESS[reg]
    ranges = [ range(0, 6), range(6, 17), range(17, 23), [255] ]
    for (i, r) in enumerate(ranges):
        if current_page in r:
            if (read):
                assert(readable_pages & (1 << i) > 0)
            if (write):
                assert(writeable_pages & (1 << i) > 0)

def fanctrl_write(command, data=[]):
    (reg, n_bytes) = command
    assert_page_ok(reg, write=True)
    
    smbus_write(FANCTRL_ADDR, reg, data, n_bytes)

def fanctrl_read(command):
    (reg, n_bytes) = command
    assert_page_ok(reg, read=True)
    
    return smbus_read(FANCTRL_ADDR, reg, n_bytes)
    
def fanctrl_read_as_val(command):
    return join_as_val(fanctrl_read(command))
    
def fanctrl_read_as_str(command):
    return join_as_string(fanctrl_read(command))
    
def fanctrl_set_page(page):
    global current_page
    current_page = page
    fanctrl_write(FANCTRL_PAGE, [page & 0xFF])
    
def fanctrl_set_pwm(pwm):
    assert(pwm >= 0 and pwm <= 1)
    pwm_val = int(round(0x2710 * pwm))
    fanctrl_write(FANCTRL_FAN_COMMAND_1, split_as_bytes(pwm_val, 2))
