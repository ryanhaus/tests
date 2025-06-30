#!/usr/bin/env python3
from i2c_aardvark import *
from pca9551 import *
from at24c128 import *
from max31785 import *

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
        val = eeprom_read_random(i, 1)[0]
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
    
    for (i, val) in enumerate(vals):
        assert(val == i & 0xFF)
        
    print("All values read OK")
 


    # Fan Controller
    #fanctrl_write(FANCTRL_RESTORE_DEFAULT_ALL)
    #sleep(0.25)
    print("Reading from fan controller")
    fanctrl_set_page(0)    
    status = fanctrl_read_as_val(FANCTRL_STATUS_BYTE)
    status_word = fanctrl_read_as_val(FANCTRL_STATUS_WORD)
    print(f"Status: 0x{status:02X}/0x{status_word:04X}")
    
    mfr_id = fanctrl_read_as_val(FANCTRL_MFR_ID)
    print(f"Manufacturer ID: 0x{mfr_id:02X}")
    
    mfr_model = fanctrl_read_as_val(FANCTRL_MFR_MODEL)
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
    
    pos = fanctrl_read_as_val(FANCTRL_MFR_TIME_COUNT)
    pos_days = pos / (24 * 60 * 60)
    print(f"Power on time: {pos} seconds ({pos_days:.2f} days)")
    
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
            
            fanctrl_set_pwm(0.25)
            
            fan_speed = fanctrl_read_as_val(FANCTRL_READ_FAN_SPEED_1)
            print(f"Fan speed: {fan_speed} RPM")
            
            # PWM is read in units of 0.01%
            fan_pwm = fanctrl_read_as_val(FANCTRL_MFR_READ_FAN_PWM) / 100
            print(f"Fan PWM: {fan_pwm}%")
            
            fan_run_time = fanctrl_read_as_val(FANCTRL_MFR_FAN_RUN_TIME)
            print(f"Fan run time: {fan_run_time} hour(s)")
        
        # temperature sensor pages
        if page in [6, 7, 12]:
            fanctrl_write(FANCTRL_MFR_TEMP_SENSOR_CONFIG, 0x8000)
            
            # temp is read in units of 0.01 deg C
            temperature = fanctrl_read_as_val(FANCTRL_READ_TEMPERATURE_1) / 100
            print(f"Temperature: {temperature} deg C")
            
        # ADC pages
        if page in [20, 21]:
            # voltage is read in units of mV
            voltage = fanctrl_read_as_val(FANCTRL_READ_VOUT) / 1000
            print(f"Voltage: {voltage} V")
    
    while True:
        input_str = input("Enter command (? for help): ")
        
        if input_str == "?":
            print("commands:")
            print("?                display this menu")
            print("set_pwm          sets the fan PWMs")
            print("read_rpm         reads the fan RPMs")
            print("read_rpm_avg     reads the fan RPMs averaged over a given time")
            print("exit             exits program")
        
        elif input_str == "set_pwm":
            pwm = float(input("Enter PWM (%): ")) / 100.0
            
            assert(pwm >= 0.0 and pwm <= 1.0)
            
            for page in [0, 1, 2, 3]:
                fanctrl_set_page(page)
                fanctrl_set_pwm(pwm)
        
        elif input_str == "read_rpm":
            for page in [0, 1, 2, 3]:
                fanctrl_set_page(page)
                rpm = fanctrl_read_as_val(FANCTRL_READ_FAN_SPEED_1)
                
                print(f"Page {page}: {rpm} RPM")
        
        elif input_str == "read_rpm_avg":
            sample_delay = float(input("Enter sample delay (s): "))
            n_samples = int(input("Enter number of samples: "))
            
            rpm_totals = [0, 0, 0, 0]
            
            for i in range(n_samples):
                for page in [0, 1, 2, 3]:
                    fanctrl_set_page(page)
                    rpm = fanctrl_read_as_val(FANCTRL_READ_FAN_SPEED_1)
                    rpm_totals[page] += rpm
                    
                sleep(sample_delay)
                
            for page in [0, 1, 2, 3]:
                avg_rpm = rpm_totals[page] / n_samples
                print(f"Page {page}: {avg_rpm} RPM")
            
        elif input_str == "exit":
            break
            
        else:
            print("Invalid command")
        
        print()
            
 
    i2c_deinit()
 
if __name__ == "__main__":
    main()
