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
        if mode == "dht11":
            pin = config.get("pin", 21)
            chip = config.get("chip", 0)
            gpio_handle = lgpio.gpiochip_open(chip)
            primary = DHTAdapter(pin=pin, gpio_handle=gpio_handle)
            secondary = ADSAdapter()
            # wrap both sensors together so if primary fails, we try secondary
            return FallbackTemperatureSensor(primary, secondary, gpio_handle=gpio_handle)

        # so bc DHT is the one that fails and ads, does not, did not include redundancy for this
        elif mode == "ads":
            return ADSAdapter()

        # Prolly config file is wrong, so make sure mode is correct in config.json
        else:
            raise ValueError(f"Unknown sensor mode: '{mode}'")