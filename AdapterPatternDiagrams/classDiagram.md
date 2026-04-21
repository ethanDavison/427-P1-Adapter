````mermaid
classDiagram
    class TemperatureSensor {

        +get_temperature(self)
    }

    class ADSAdapter {
        -ADS1110 driver
        +__init__(self)
        +get_temperature(self)
    }

    class DHTAdapter {
        -DHT11 driver
        +__init__(pin, gpio_handle)
        +get_temperature()
    }

    class ADS1110 {
        -int addr
        -int config_value
        -int handle
        +__init__(self)
        +read_raw(self)
        +close(self)
    }

    class DHT11 {
        -int __pin
        -gpio __gpio
        +__init__(pin, gpio)
        +read(self)
        -__send_and_sleep(self,output, sleep_time)
        -__collect_input(self)
        -__parse_data_pull_up_lengths(self,data)
        -__calculate_bits(self,pull_up_lengths)
        -__bits_to_bytes(self,bits)
        -__calculate_checksum(self,the_bytes)
    }

    class DHT11Result {
        +int ERR_NO_ERROR
        +int ERR_MISSING_DATA
        +int ERR_CRC
        +int error_code
        +int temperature
        +int humidity
        +__init__(error_code, temperature, humidity)
        +is_valid()
    }

    %% Not entirely sure how to show this, as its not a class but essential to this project to get readings
    class lgpio {
    - external library
    -allows hardware access to raspberry PI and GPIO pins
}



    %% So basically get_temperature in TempteratureSensor is ajust a interface to show how the function should look in both ADSAdapter and DHTAdapter
    TemperatureSensor <|-- ADSAdapter : inherit Temperature Sensor interface
    TemperatureSensor <|-- DHTAdapter : inherit Temperature Sensor interface

    ADSAdapter ..> ADS1110 : uses
    DHTAdapter ..> DHT11 : uses

    ADS1110 ..> lgpio : relies on
    DHT11 ..> lgpio : relies on

    DHT11 ..> DHT11Result : creates/returns
    ```
````
