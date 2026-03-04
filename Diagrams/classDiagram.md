````mermaid
classDiagram
    class TemperatureSensor {
        +get_temperature(self)
        +cleanup(self)
    }

    class SensorFactory {
        +create_sensor(config)$
    }

    class FallbackTemperatureSensor {
        -primary
        -secondary
        -gpio_handle
        +__init__(primary, secondary, gpio_handle)
        +get_temperature(self)
        +cleanup(self)
    }

    class ADSAdapter {
        -ADS1110 driver
        +__init__(self)
        +get_temperature(self)
    }

    class DHTAdapter {
        -DHT11 driver
        +__init__(pin, gpio_handle)
        +get_temperature(self)
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
    }

    class DHT11Result {
        +int ERR_NO_ERROR
        +int ERR_MISSING_DATA
        +int ERR_CRC
        +int temperature
        +int humidity
        +is_valid()
    }

    class lgpio {
        external library
    }

    TemperatureSensor <|-- ADSAdapter
    TemperatureSensor <|-- DHTAdapter
    TemperatureSensor <|-- FallbackTemperatureSensor

    SensorFactory ..> FallbackTemperatureSensor : creates
    SensorFactory ..> DHTAdapter : creates
    SensorFactory ..> ADSAdapter : creates

    FallbackTemperatureSensor o-- ADSAdapter : secondary
    FallbackTemperatureSensor o-- DHTAdapter : primary

    ADSAdapter ..> ADS1110 : uses
    DHTAdapter ..> DHT11 : uses
    ADS1110 ..> lgpio : relies on
    DHT11 ..> lgpio : relies on
    DHT11 ..> DHT11Result : creates/returns
    ```
````
