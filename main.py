import lgpio
import time

def main():
    pin = 21
    gpio = lgpio.gpiochip_open(0)  # Open the GPIO chip
    lgpio.gpio_claim_output(gpio, pin)  # Set pin as output
    myDHT = DHT11(pin, gpio)  # Pass the gpio handle to DHT11

    addr = 0x48
    config = 0b0_00_0_11_00
    myADS = ADS1110(addr, config)
    try:
        while True:
            resultDHT = myDHT.read()
            resultADS = myADS.read()

            if resultADS and resultDHT.is_valid():
                print(f'DHTtemp = {resultDHT.temperature}  ADStemp = {resultADS:04x}')
                #WIP, CHANGE resultDHT.temperature AND resultADS TO F*!!
            else: #WIP, STUFF HERE FOR USING ONE WHEN THE OTHER FAILS
                pass
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting.")
    finally:
        lgpio.gpiochip_close(gpio)  # Close GPIO chip when done
        myADS.close()



# DHT Section-----------------------------------------------------------------------------------------

class DHT11Result:
    'DHT11 sensor result returned by DHT11.read() method'

    ERR_NO_ERROR = 0
    ERR_MISSING_DATA = 1
    ERR_CRC = 2

    error_code = ERR_NO_ERROR
    temperature = -1
    humidity = -1

    def __init__(self, error_code, temperature, humidity):
        self.error_code = error_code
        self.temperature = temperature
        self.humidity = humidity

    def is_valid(self):
        #if not self.error_code == DHT11Result.ERR_NO_ERROR:
        #    print(self.error_code, end=" ")
        return self.error_code == DHT11Result.ERR_NO_ERROR


class DHT11:
    __pin = 0
    __gpio = None

    def __init__(self, pin, gpio):
        self.__pin = pin
        self.__gpio = gpio

    def read(self):
        lgpio.gpio_claim_output(self.__gpio, self.__pin)

        # send initial high
        self.__send_and_sleep(lgpio.HIGH, 0.05)

        # pull down to low
        self.__send_and_sleep(lgpio.LOW, 0.02)

        # change to input using pull up
        lgpio.gpio_claim_input(self.__gpio, self.__pin)

        # collect data into an array
        data = self.__collect_input()

        # parse lengths of all data pull up periods
        pull_up_lengths = self.__parse_data_pull_up_lengths(data)

        # if bit count mismatch, return error (4 byte data + 1 byte checksum)
        if len(pull_up_lengths) != 40:
            print('Incorrect data length: ', len(pull_up_lengths))
            return DHT11Result(DHT11Result.ERR_MISSING_DATA, 0, 0)

        # calculate bits from lengths of the pull up periods
        bits = self.__calculate_bits(pull_up_lengths)

        # we have the bits, calculate bytes
        the_bytes = self.__bits_to_bytes(bits)

        # calculate checksum and check
        checksum = self.__calculate_checksum(the_bytes)
        if the_bytes[4] != checksum:
            return DHT11Result(DHT11Result.ERR_CRC, 0, 0)

        # ok, we have valid data

        # The meaning of the return sensor values
        # the_bytes[0]: humidity int
        # the_bytes[1]: humidity decimal
        # the_bytes[2]: temperature int
        # the_bytes[3]: temperature decimal

        temperature = the_bytes[2] + float(the_bytes[3]) / 10
        humidity = the_bytes[0] + float(the_bytes[1]) / 10

        return DHT11Result(DHT11Result.ERR_NO_ERROR, temperature, humidity)

    def __send_and_sleep(self, output, sleep_time):
        lgpio.gpio_write(self.__gpio, self.__pin, output)
        time.sleep(sleep_time)

    def __collect_input(self):
        # collect the data while unchanged found
        unchanged_count = 0

        # this is used to determine where is the end of the data
        max_unchanged_count = 100

        last = -1
        data = []
        while True:
            current = lgpio.gpio_read(self.__gpio, self.__pin)
            data.append(current)
            if last != current:
                unchanged_count = 0
                last = current
            else:
                unchanged_count += 1
                if unchanged_count > max_unchanged_count:
                    break

        return data

    def __parse_data_pull_up_lengths(self, data):
        STATE_INIT_PULL_DOWN = 1
        STATE_INIT_PULL_UP = 2
        STATE_DATA_FIRST_PULL_DOWN = 3
        STATE_DATA_PULL_UP = 4
        STATE_DATA_PULL_DOWN = 5

        state = STATE_INIT_PULL_DOWN
        lengths = []  # will contain the lengths of data pull up periods
        current_length = 0  # will contain the length of the previous period

        for i in range(len(data)):
            current = data[i]
            current_length += 1

            if state == STATE_INIT_PULL_DOWN:
                if current == lgpio.LOW:
                    # ok, we got the initial pull down
                    state = STATE_INIT_PULL_UP
                    continue
                else:
                    continue
            if state == STATE_INIT_PULL_UP:
                if current == lgpio.HIGH:
                    # ok, we got the initial pull up
                    state = STATE_DATA_FIRST_PULL_DOWN
                    continue
                else:
                    continue
            if state == STATE_DATA_FIRST_PULL_DOWN:
                if current == lgpio.LOW:
                    # we have the initial pull down, the next will be the data pull up
                    state = STATE_DATA_PULL_UP
                    continue
                else:
                    continue
            if state == STATE_DATA_PULL_UP:
                if current == lgpio.HIGH:
                    # data pulled up, the length of this pull up will determine whether it is 0 or 1
                    current_length = 0
                    state = STATE_DATA_PULL_DOWN
                    continue
                else:
                    continue
            if state == STATE_DATA_PULL_DOWN:
                if current == lgpio.LOW:
                    # pulled down, we store the length of the previous pull up period
                    lengths.append(current_length)
                    state = STATE_DATA_PULL_UP
                    continue
                else:
                    continue

        return lengths

    def __calculate_bits(self, pull_up_lengths):
        # find shortest and longest period
        shortest_pull_up = 1000
        longest_pull_up = 0

        for i in range(0, len(pull_up_lengths)):
            length = pull_up_lengths[i]
            if length < shortest_pull_up:
                shortest_pull_up = length
            if length > longest_pull_up:
                longest_pull_up = length

        # use the halfway to determine whether the period it is long or short
        #halfway = shortest_pull_up + (longest_pull_up - shortest_pull_up) / 2
        halfway = shortest_pull_up + (longest_pull_up - shortest_pull_up) >> 1
        bits = []

        for i in range(0, len(pull_up_lengths)):
            bit = False
            if pull_up_lengths[i] > halfway:
                bit = True
            bits.append(bit)

        return bits

    def __bits_to_bytes(self, bits):
        the_bytes = []
        byte = 0

        for i in range(0, len(bits)):
            byte = byte << 1
            if bits[i]:
                byte = byte | 1
            else:
                byte = byte | 0
            if (i + 1) % 8 == 0:
                the_bytes.append(byte)
                byte = 0

        return the_bytes

    def __calculate_checksum(self, the_bytes):
        return the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3] & 255



# ADS Section-----------------------------------------------------------------------------------------

class ADS1110:
    __CONFIG_VALUE = 0b0_00_0_11_00
    __ADS1110_ADDR = 0x48
    __handle = 0

    def __init__(self, addr, config):
        self.__ADS1110_ADDR = addr
        self.__CONFIG_VALUE = config

        # Initialize the connection to lgpio
        try:
            # Open connection to the I2C port
            self.__handle = lgpio.i2c_open(1, self.__ADS1110_ADDR)
            print(f"I2C connection to address 0x{self.__ADS1110_ADDR:02x} opened.")

            # Write data to the configuration register
            result = lgpio.i2c_write_byte(self.__handle, __CONFIG_VALUE)
            
            if result == 0:
                pass
                #print(f"Configuration written: {__CONFIG_VALUE}")
            else:
                print(f"Write error: code {result}")
                raise IOError("Configuration write error")

            # Time for conversion (may be required, check the datasheet)
            time.sleep(0.1)

        except IOError as e:
            print(f"I/O error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def close(self):
        # Close the I2C connection
        if self.__handle >= 0:
            lgpio.i2c_close(self.__handle)
        print("Connection to lgpio closed.")

    def read(self):
        # Read 2 bytes (unchanged in this example)
        count, data = lgpio.i2c_read_device(self.__handle, 2)
        
        if count == 2:
            # Combine two bytes into one value (little-endian)
            raw_value = (data[0] << 8) | data[1]
            # two’s complement conversion
            if raw_value & 0x8000:
                raw_value -= 1 << 16
            return raw_value
        else:
            return False



main()
