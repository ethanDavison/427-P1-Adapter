import time
from ads1110lgpio import ADS1110
from dh11_lgpio import DHT11
import lgpio

# The Unifed Base Class
class TemperatureSensor:
    def get_temperature(self):
        pass

    def open(self):
        pass

    def close(self):
        pass

# Adapter for Analog 
class ADSAdapter(TemperatureSensor):
    def __init__(self):
        self.driver = None
    
    def open(self):
        self.driver = ADS1110()

    def close(self):
        self.driver.close()

    def get_temperature(self):
        try:
            raw = self.driver.read_raw()
            if raw != None:
                # I could be wrong on this but 1st convert raw to volatage
                # 32767 is Max code for 16-bit, Internal Referenace Volatage 
                vol = raw / 32767 * 2.048
                # 1 vol = 1000mV, and 10mV per Degree Cel
                temp_c = vol * 1000 / 10
                return temp_c
        except Exception as e: 
            print(e)

        return None


# Adapter for the Digital
class DHTAdapter(TemperatureSensor):
    def __init__(self, pin, gpio_handle):
        self.driver = None
        self._pin = pin
        self._gpio_handle = gpio_handle


    def open(self):
        self.driver = DHT11(self._pin, self._gpio_handle)

    def close(self):  
        if self._gpio_handle is not None:
            lgpio.gpiochip_close(self._gpio_handle)
            self._gpio_handle = None

    def get_temperature(self):
        try:
            result = self.driver.read()
            if result.is_valid():
                # right now am only pulling out the temperature but could
                # pull out the humidity as well and display that
                return result.temperature
        except Exception as e: 
            print(e)
        # cant hurt to wait a lil bit between calls
        return None