import lgpio
from adapters import ADSAdapter, DHTAdapter


# existing base class
class TemperatureSensor:
    def get_temperature(self):
        pass

    def cleanup(self):
        pass


# tries primary first, secondary if primary returns None
class FallbackTemperatureSensor(TemperatureSensor):
   # gpio_handle is optional, only needed for DHT11 to close the GPIO pin on cleanup
    def __init__(self, primary, secondary, gpio_handle=None):
        self.primary = primary
        self.secondary = secondary
        self._gpio_handle = gpio_handle

    def get_temperature(self):
        temp = self.primary.get_temperature()
        if temp is None:
            print("Primary sensor failed, falling back to secondary...")
            return self.secondary.get_temperature()
        
        return temp
    
    # ONLY NEED THIS TO CLEAN UP DHT11 SENSOR
    def cleanup(self):
        # bc I have this check here, in main i can always call this and will not have any problems
        if self._gpio_handle is not None:
            lgpio.gpiochip_close(self._gpio_handle)
            self._gpio_handle = None


class SensorFactory:
    @staticmethod
    def create_sensor(config) -> TemperatureSensor:
        mode = config.get("mode")
        pin = config.get("pin", 21)
        chip = config.get("chip", 0)
        if mode == "dht11":
            gpio_handle = lgpio.gpiochip_open(chip)
            primary = DHTAdapter(pin=pin, gpio_handle=gpio_handle)
            secondary = ADSAdapter()
            # wrap both sensors together so if primary fails, we try secondary
            return FallbackTemperatureSensor(primary, secondary, gpio_handle=gpio_handle)

        #  Included redundancy for ads aswell, will not get triggered but thats fine
        elif mode == "ads":
            gpio_handle = lgpio.gpiochip_open(chip)
            primary = ADSAdapter()
            secondary = DHTAdapter(pin=pin, gpio_handle=gpio_handle)
            return FallbackTemperatureSensor(primary, secondary, gpio_handle=gpio_handle)

        # Prolly config file is wrong, so make sure mode is correct in config.json
        else:
            raise ValueError(f"Unknown sensor mode: '{mode}'")