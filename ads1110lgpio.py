import lgpio
import time

class ADS1110:
    def __init__(self):
        ### Config that Pach had ####
        # I2C address of ADS1110
        self.addr = 0x48 
        # Value to write to the configuration register
        self.config_value = 0b0_00_0_11_00

        # Pre set this value to -1 for checks below when reading the sensor value to avoid possible crash
        self.handle = -1
        
        try:
            # Open connection to the I2C port
            self.handle = lgpio.i2c_open(1, self.addr)
            # Write data to the configuration register
            lgpio.i2c_write_byte(self.handle, self.config_value)
            # Time for conversion (may be required, check the datasheet)
            time.sleep(0.1)
        except Exception as e:
            print(f"Configuration write error: {e}")

    # Moved Functionality into a function to read the "raw" sensor data
    def read_raw(self):
        if self.handle < 0:
            return None
        #### got rid of while Loop  
        try:
            # Read data from the device
            count, data = lgpio.i2c_read_device(self.handle, 2)
            if count == 2:
                # Combine two bytes into one value (little-endian)
                raw_value = (data[0] << 8) | data[1]
                # two’s complement conversion
                if raw_value & 0x8000:
                    raw_value -= 1 << 16
                return raw_value
        except Exception:
            return None
        return None

    # Close the I2C connection
    def close(self):
        if self.handle >= 0:
            lgpio.i2c_close(self.handle)
