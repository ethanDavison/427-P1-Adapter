import lgpio
from adapters import ADSAdapter, DHTAdapter, TemperatureSensor
from decorators import RetryDecorator, FallbackDecorator




class SensorFactory:
    @staticmethod
    def create_sensor(config) -> TemperatureSensor:
        mode = config.get("mode")
        pin = config.get("pin", 21)
        chip = config.get("chip", 0)
        if mode == "dht11":
            gpio_handle = lgpio.gpiochip_open(chip)
            sensors = [
            RetryDecorator(DHTAdapter(pin=pin, gpio_handle=gpio_handle), retries=3),
            RetryDecorator(ADSAdapter(), retries=3),
            ]
            # return FallbackDecorator object 
            return FallbackDecorator(sensors)


        # warp ADS sensor in retry Decorator object
        elif mode == "ads":
            gpio_handle = lgpio.gpiochip_open(chip)
            sensors = [
            RetryDecorator(ADSAdapter(), retries=3),
            RetryDecorator(DHTAdapter(pin=pin, gpio_handle=gpio_handle), retries=3)
            ]
            # return FallbackDecorator object 
            return FallbackDecorator(sensors)

        # Prolly config file is wrong, so make sure mode is correct in config.json
        else:
            raise ValueError(f"Unknown sensor mode: '{mode}'")