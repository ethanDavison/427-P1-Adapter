from adapters import TemperatureSensor

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
    def cleanup(self):
        self._wrapped.cleanup()

class FallbackDecorator(TemperatureSensor):
    def __init__(self,sensors: list[TemperatureSensor]):
        self._sensors = sensors

    def get_temperature(self):
        for sensor in self._sensors:
            temp = sensor.get_temperature()
            if temp is not None:
                return temp
        return None

    # dont know if this is supposed to be here, but moved it here so we can close for DHT11
    def cleanup(self):
        for sensor in self._sensors:
            sensor.cleanup()