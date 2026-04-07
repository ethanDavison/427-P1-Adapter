import socket
import json
import datetime
import time
import random

# this has to be the same PV4 address as the machine that is running docker
BRAIN_HOST = "10.36.224.120"
BRAIN_PORT = 5000
PI_ID = "Pi_B"


while True:
    # generate a fake temperature reading
    fake_temp = round(random.uniform(20.0, 35.0), 2)
    
    dto = {
        "origin": PI_ID,
        "payload": {"temp": fake_temp, "unit": "C"},
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((BRAIN_HOST, BRAIN_PORT))
            s.sendall(json.dumps(dto).encode())
            print(f"Sent: {dto}")
    except Exception as e:
        print(f"Failed to send: {e}")

    time.sleep(2)