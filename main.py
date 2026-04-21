import time
import json
import socket
import datetime
from sensor_factory import SensorFactory

# load in the config.json file
def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)

def send_to_brain(temp_c, pi_id, host, port):
    # package the reading as a DTO and send to brain over TCP
    dto = {
        "origin": pi_id,
        "payload": {"temp": round(temp_c, 2), "unit": "C"},
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(json.dumps(dto).encode())
    except Exception as e:
        print(f"Failed to send to brain: {e}")

# load our config and sensor from config
config = load_config()
sensor = SensorFactory.create_sensor(config)
sensor.open()


PI_ID = config.get("pi_id", "Pi_A")
BRAIN_HOST = config.get("brain_host", "192.168.1.45")
BRAIN_PORT = config.get("brain_port", 5000)

# where we get the temp reading
try:
    while True:
        temp = sensor.get_temperature()
        if temp is not None:
            temp_f = round(temp * 1.8 + 32, 2)
            print(f"Reading: {temp_f}°F")
            # send reading to brain as JSON over TCP
            send_to_brain(temp, PI_ID, BRAIN_HOST, BRAIN_PORT)
except KeyboardInterrupt:
    print("Exiting.")
finally:
    sensor.close()