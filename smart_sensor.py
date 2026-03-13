import time
from adapters import TemperatureSensor



# every filter class we add , rn only MeanFIlter, must have a filter method
class FilterStrategy:
    def filter(self, buffer: list) -> float:
        pass

# Decided to do mean
class MeanFilter(FilterStrategy):
    # takes in buffer (list) sums all the values and dives by length to get average
    def filter(self, buffer: list) -> float:
        return sum(buffer) / len(buffer)
    
# if we wanted other methods add other classes below here



class SmartSensor(TemperatureSensor):
    def __init__(self, sensor: TemperatureSensor, strategy: FilterStrategy, buffer_size: int = 10):
        self._sensor = sensor
        self._strategy = strategy
        self._buffer = []
        self._buffer_size = buffer_size

        self._timestamps = []

    # passed down from adapter
    def open(self):
        self._sensor.open()

    # passed down from adapter
    def close(self):
        self._sensor.close()

    def get_temperature(self):
        # get our raw reading
        raw = self._sensor.get_temperature()

        if raw is not None:
            # add this reading to the buffer list
            self._buffer.append(raw)
            # if list is now above our max size, pop the oldest reading
            if len(self._buffer) > self._buffer_size:
                self._buffer.pop(0) 
            # use time to get the time of the reading, and add to the timestamp list
            self._timestamps.append(time.time())
            if len(self._timestamps) > self._buffer_size:
                # if greater than max buffer size, remove oldest.
                self._timestamps.pop(0)

        # WILL not happen buf if every temptature reading failed, just return Non
        if len(self._buffer) == 0:
            return None
        # return the buffer to our stat, which returns to Retry Decorator, FallbackDecorator, and main
        return self._strategy.filter(self._buffer)