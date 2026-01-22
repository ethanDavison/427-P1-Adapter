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
        raw = self.driver.read_raw()
        # I could be wrong on this but 1st convert raw to volatage
        # 32767 is Max code for 16-bit, Internal Referenace Volatage 
        vol = raw / 32767 * 2.048
        # 1 vol = 1000mV, and 10mV per Degree Cel
        temp_c = vol * 1000 / 10
        return temp_c

# Adapter for the Digital
class DHTAdapter(TemperatureSensor):
    def __init__(self, pin, gpio_handle):
        self.driver = DHT11(pin, gpio_handle)

    def get_temperature(self):
        result = self.driver.read()
        if result.is_valid():
            # right now am only pulling out the temperature but could
            # pull out the humidity as well and display that
            return result.temperature
        return None
