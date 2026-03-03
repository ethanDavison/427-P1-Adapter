from adapters import TemperatureSensor
import lgpio

class RetryDecorator(TemperatureSensor):
    def __init__(self, wrapped: TemperatureSensor, retries: int = 3):
        self._wrapped = wrapped
        self._retries = retries

    def get_temperature(self):
        for _ in range(self._retries):
            temp = self._wrapped.get_temperature()
            if temp is not None:
                return temp
        return None

class FallbackDecorator(TemperatureSensor):
    def __init__(self, primary: TemperatureSensor, secondary: TemperatureSensor, gpio_handle=None):
        self._primary = primary
        self._secondary = secondary
        self._gpio_handle = gpio_handle

    def get_temperature(self):
        temp = self._primary.get_temperature()
        if temp is None:
            print("Primary sensor failed, falling back to secondary...")
            return self._secondary.get_temperature()
        return temp

    # dont know if this is supposed to be here, but moved it here so we can close for DHT11
    def cleanup(self):
        if self._gpio_handle is not None:
            lgpio.gpiochip_close(self._gpio_handle)
            self._gpio_handle = None