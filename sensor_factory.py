import lgpio
from adapters import ADSAdapter, DHTAdapter
from decorators import RetryDecorator, FallbackDecorator


# existing base class
class TemperatureSensor:
    def get_temperature(self):
        pass



class SensorFactory:
    @staticmethod
    def create_sensor(config) -> TemperatureSensor:
        mode = config.get("mode")
        pin = config.get("pin", 21)
        chip = config.get("chip", 0)
        if mode == "dht11":
            gpio_handle = lgpio.gpiochip_open(chip)
            # wrap these in retry Decorator class 
            primary = RetryDecorator(DHTAdapter(pin=pin, gpio_handle=gpio_handle), retries=3)
            secondary = RetryDecorator(ADSAdapter(), retries=3)
            # return FallbackDecorator object with gpio Handle
            return FallbackDecorator(primary, secondary, gpio_handle=gpio_handle)


        # warp ADS sensor in retry Decorator object
        elif mode == "ads":
            gpio_handle = lgpio.gpiochip_open(chip)
            # wrap these in retry Decorator class 
            primary = RetryDecorator(ADSAdapter(), retries=3)
            secondary = RetryDecorator(DHTAdapter(pin=pin, gpio_handle=gpio_handle), retries=3)
            # return FallbackDecorator object with gpio Handle
            return RetryDecorator(primary, secondary, gpio_handle=gpio_handle)

        # Prolly config file is wrong, so make sure mode is correct in config.json
        else:
            raise ValueError(f"Unknown sensor mode: '{mode}'")