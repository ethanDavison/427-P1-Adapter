import time
import json
from sensor_factory import SensorFactory

# load in the config.json file
def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)

# load our config and sensor from config
config = load_config()
sensor = SensorFactory.create_sensor(config)

# where we get the temp reading
try:
    while True:
        temp = sensor.get_temperature()
        if temp is not None:
            temp_f = round(temp * 1.8 + 32, 2)
            print(f"Reading: {temp_f}°F")
        time.sleep(0.1)
except KeyboardInterrupt:
    sensor.cleanup()
    print("Exiting.")