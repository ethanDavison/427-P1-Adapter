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
    
    def open(self):
        self._wrapped.open()

    def close(self):
        self._wrapped.close()


class FallbackDecorator(TemperatureSensor):
    def __init__(self,sensors: list[TemperatureSensor]):
        self._sensors = sensors

    def get_temperature(self):
        for sensor in self._sensors:
            temp = sensor.get_temperature()
            if temp is not None:
                return temp
        return None
    
    def open(self):
        for sensor in self._sensors:
            sensor.open()

    def close(self):
        for sensor in self._sensors:
            sensor.close()