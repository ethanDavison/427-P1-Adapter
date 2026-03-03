import time
from ads1110lgpio import ADS1110
from dh11_lgpio import DHT11

# The Unifed Base Class
class TemperatureSensor:
    def get_temperature(self):
        pass

# Adapter for Analog 
class ADSAdapter(TemperatureSensor):
    def __init__(self):
        self.driver = ADS1110()

    def get_temperature(self):
        # Loop 3 times before we send NONE back
        for attempt in range(3):
            try:
                raw = self.driver.read_raw()
                if raw != None:
                    # I could be wrong on this but 1st convert raw to volatage
                    # 32767 is Max code for 16-bit, Internal Referenace Volatage 
                    vol = raw / 32767 * 2.048
                    # 1 vol = 1000mV, and 10mV per Degree Cel
                    temp_c = vol * 1000 / 10
                    return temp_c
            except:
                pass
            # cant hurt to wait a lil bit between calls
            time.sleep(0.1)
        return None


# Adapter for the Digital
class DHTAdapter(TemperatureSensor):
    def __init__(self, pin, gpio_handle):
        self.driver = DHT11(pin, gpio_handle)

    def get_temperature(self):
        # try 3 times before we return invalid result
        for attempt in range(3):
            try:
                result = self.driver.read()
                if result.is_valid():
                    # right now am only pulling out the temperature but could
                    # pull out the humidity as well and display that
                    return result.temperature
            except:
                pass
            # cant hurt to wait a lil bit between calls
            time.sleep(0.1)
        return None