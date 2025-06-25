#!/usr/bin/env python3
from aardvark_py import *
from time import sleep



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
    
    return data if n_bytes > 1 else data[0]
# End Aardvark abstraction



# SMBus
def smbus_write(addr, reg, data=[], n_bytes=-1):
    if not isinstance(data, list):
        assert(n_bytes > 0)
        data = split_as_bytes(data, n_bytes)
        
    data.insert(0, reg)
    i2c_write(addr, data)
 
def smbus_read(addr, reg, n_bytes=1):
    i2c_write(addr, [reg], flags=AA_I2C_NO_STOP)
    return i2c_read(addr, n_bytes)
# End SMBus



# LED Controller
# PCA9551
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
# End LED Controller



# EEPROM
# AT24C128
EEPROM_ADDR = 0x54
T_WR = 0.01 # EEPROM write time

def eeprom_write(addr, data=[], n_bytes=-1):
    if not isinstance(data, list):
        assert(n_bytes > 0)
        
        data = split_as_bytes(data, n_bytes)
        
    if len(data) > 64:
        eeprom_write(addr, data[0:63])
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
# End EEPROM



# Fan Controller
# MAX31785
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
# End Fan Controller



# Util
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
# End Util



def main():
    i2c_init()
 
    # LED Controller (PCA9551)
    print("Making LED controller blink...")
    ledctrl_write(LEDCTRL_LS0, 0x0A)
    ledctrl_write(LEDCTRL_PSC0, 0x10)
 
    # EEPROM
    print("Writing to EEPROM 0x0000...")
    eeprom_write(0x0000, [0x12, 0x34, 0x56, 0x78])
    
    print("Reading from EEPROM 0x0000....")
    print("Random reads:")
    
    for i in range(4):
        val = eeprom_read_random(i, 1)
        print(f"0x{i:04X}: 0x{val:02X}")
        
    print("Multiple byte read:")
    vals = eeprom_read_random(0x0000, 4)
    for (i, val) in enumerate(vals):
        print(f"0x{i:04X}: 0x{val:02X}")
    
    print("Writing many values to EEPROM 0x1000...")
    vals = list(map(lambda x: x & 0xFF, range(0, 0x200)))
    eeprom_write(0x1000, vals)
    
    print("Reading many values from EEPROM 0x1000...")
    vals = eeprom_read_random(0x1000, 0x200)
    print(vals)
 
    # Fan Controller
    #fanctrl_write(FANCTRL_RESTORE_DEFAULT_ALL)
    #sleep(0.25)
    
    print("Reading from fan controller")
    fanctrl_set_page(0)    
    status = fanctrl_read(FANCTRL_STATUS_BYTE)
    status_word = fanctrl_read_as_val(FANCTRL_STATUS_WORD)
    print(f"Status: 0x{status:02X}/0x{status_word:04X}")
    
    mfr_id = fanctrl_read(FANCTRL_MFR_ID)
    print(f"Manufacturer ID: 0x{mfr_id:02X}")
    
    mfr_model = fanctrl_read(FANCTRL_MFR_MODEL)
    print(f"Manufacturer model: 0x{mfr_model:02X}")
    
    mfr_revision = fanctrl_read_as_val(FANCTRL_MFR_REVISION)
    print(f"Manufacturer revision: 0x{mfr_revision:04X}")
    
    mfr_location = fanctrl_read_as_str(FANCTRL_MFR_LOCATION)
    print(f"Manufacturer location: {mfr_location}")
    
    mfr_date = fanctrl_read_as_str(FANCTRL_MFR_DATE)
    print(f"Manufacturer date: {mfr_date}")
    
    mfr_serial = fanctrl_read_as_str(FANCTRL_MFR_SERIAL)
    print(f"Manufacturer serial: {mfr_serial}")
    
    mfr_mode = fanctrl_read_as_val(FANCTRL_MFR_MODE)
    print(f"Manufacturer mode: 0x{mfr_mode:04X}")
    
    fanctrl_write(FANCTRL_MFR_MODE, 0x007F)
    
    # Vout scaling
    fanctrl_set_page(20)
    fanctrl_write(FANCTRL_VOUT_SCALE_MONITOR, 0x26C8)
    
    fanctrl_set_page(21)
    fanctrl_write(FANCTRL_VOUT_SCALE_MONITOR, 0x0AAB)
        
    for page in [0, 1, 2, 3, 6, 7, 12, 20, 21]:
        print(f"\nPage {page}")
        fanctrl_set_page(page)
        
        # fan pages
        if page in [0, 1, 2, 3]:
            fanctrl_write(FANCTRL_MFR_FAN_CONFIG, 0xE380)
            fanctrl_write(FANCTRL_FAN_CONFIG_1_2, 0x90)
            fanctrl_set_pwm(0.5)
            
            fan_speed = fanctrl_read_as_val(FANCTRL_READ_FAN_SPEED_1)
            print(f"Fan speed: {fan_speed} RPM")
            
            fan_pwm = fanctrl_read_as_val(FANCTRL_MFR_READ_FAN_PWM) / 100
            print(f"Fan PWM: {fan_pwm}%")
            
            fan_run_time = fanctrl_read_as_val(FANCTRL_MFR_FAN_RUN_TIME)
            print(f"Fan run time: {fan_run_time} hour(s)")
        
        # temperature sensor pages
        if page in [6, 7, 12]:
            fanctrl_write(FANCTRL_MFR_TEMP_SENSOR_CONFIG, 0x8000)
            
            temperature = fanctrl_read_as_val(FANCTRL_READ_TEMPERATURE_1) / 100
            print(f"Temperature: {temperature} deg C")
            
        # ADC pages
        if page in [20, 21]:
            voltage = fanctrl_read_as_val(FANCTRL_READ_VOUT) / 1000
            print(f"Voltage: {voltage} V")
            
            vout = fanctrl_read_as_val(FANCTRL_READ_VOUT) / 1000
            print(f"Vout: {vout} V")
 
    i2c_deinit()
 
if __name__ == "__main__":
    main()