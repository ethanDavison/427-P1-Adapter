import lgpio
from adapters import ADSAdapter, DHTAdapter, TemperatureSensor
from decorators import RetryDecorator, FallbackDecorator
from smart_sensor import SmartSensor, MeanFilter




class SensorFactory:
    @staticmethod
    def create_sensor(config) -> TemperatureSensor:
        mode = config.get("mode")
        pin = config.get("pin", 21)
        chip = config.get("chip", 0)
        if mode == "dht11":
            gpio_handle = lgpio.gpiochip_open(chip)
            sensors = [
            RetryDecorator(SmartSensor(DHTAdapter(pin=pin, gpio_handle=gpio_handle),MeanFilter()), retries=3),
            RetryDecorator(SmartSensor(ADSAdapter(),MeanFilter()), retries=3),
            ]
            # return FallbackDecorator object 
            return FallbackDecorator(sensors)


        # warp ADS sensor in retry Decorator object
        elif mode == "ads":
            gpio_handle = lgpio.gpiochip_open(chip)
            sensors = [
            RetryDecorator(SmartSensor(ADSAdapter(),MeanFilter()), retries=3),
            RetryDecorator(SmartSensor(DHTAdapter(pin=pin, gpio_handle=gpio_handle),MeanFilter()), retries=3)
            ]
            # return FallbackDecorator object 
            return FallbackDecorator(sensors)

        # Prolly config file is wrong, so make sure mode is correct in config.json
        else:
            raise ValueError(f"Unknown sensor mode: '{mode}'")