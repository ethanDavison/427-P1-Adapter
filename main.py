import lgpio
import time
from adapters import ADSAdapter, DHTAdapter

# Open GPIO chip  (For dh11)
chip = lgpio.gpiochip_open(0)

# Create instanses for the adapters
analog_sensor = ADSAdapter()
digital_sensor = DHTAdapter(pin=21, gpio_handle=chip)

sensors = [analog_sensor, digital_sensor]

# each adapter shows tempture
try:
    while True:
        resultString = ""
        temp = sensors[1].get_temperature()
        name = "Digital (DHT11)"
        if temp == None:
            temp = sensors[0].get_temperature()
            name = "Analog  (LM35) "
        temp = round(temp * 1.8 + 32, 2)
        print(f"{name} Reading: {temp}\n")
        time.sleep(0.1)
except KeyboardInterrupt:
    lgpio.gpiochip_close(chip)
