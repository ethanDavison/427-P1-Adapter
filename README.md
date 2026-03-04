---
marp: true
theme: default
paginate: true
backgroundColor: #676767
color: #eaeaea
style: |
  section {
    font-family: 'Consolas', monospace;
    background-color: #1e1e2e;
    padding: 40px 60px;
  }
  h1 { color: #c0caf5; font-size: 2em; }
  h2 { color: #c0caf5; border-bottom: 2px solid #414868; padding-bottom: 8px; }
  h3 { color: #a9b1d6; }
  code { background: #24283b; padding: 2px 8px; border-radius: 4px; color: #7aa2f7; }
  pre { background: #24283b; border-left: 4px solid #414868; padding: 16px; border-radius: 8px; }
  strong { color: #7aa2f7; }
  em { color: #a9b1d6; }
---

# Temperature Sensor System

## Adapter + Factory + Decorator

**Using DHT11 and ADS sensors to read temperature from a Raspberry Pi**

---

## Previous Project - Adapter & Simple Factory Summary

### Adapter Pattern

- `DHTAdapter` and `ADSAdapter` both implement `get_temperature()` via the shared `TemperatureSensor` base class
- Each adapter retries up to 3 times before returning `None`
- `main.py` talks to either sensor the same way

### Simple Factory

- `SensorFactory.create_sensor(config)` reads `config.json` and wraps two sensors in `FallbackTemperatureSensor`
  - if primary returns `None`, it tries secondary sensor for redundancy
- `main.py` only imports `SensorFactory`

---

## Adapter & Simple Factory - Result & Issue

### Result

- Object creation fully isolated from `main.py`
- `main.py` just calls `sensor.get_temperature()`
- No hardware knowledge in the application layer

### But...

- The factory is multitasking
  - It creates sensors **AND** owns the fallback logic
- The adapters are multitasking
  - They read hardware **AND** handle retries

---

## Decorator Pattern - Why

### What is the Decorator Pattern?

- Wraps an existing object to add **new** behaviour
  - without modifying it
- Each decorator has **ONLY** one responsibility
  - seperation of concerns
- Decorators implement the **same** interface as what they wrap
  - interchangeable

### Why this fixes our problem

- Retry logic moves out of the adapters into `RetryDecorator`
  - adapters only read hardware now, **LESS** logic
- Fallback logic moves out of the factory into `FallbackDecorator`
  - **LESS** logic
- Both decorators wrap any `TemperatureSensor` — not tied to specific hardware

---

## Decorator Pattern - Implementation

### Summary

- `RetryDecorator` : wraps any `TemperatureSensor`, retries up to **N** times before returning `None`
- `FallbackDecorator` : takes a **list** of sensors, tries each one in order until it gets a reading
- Adapters **stripped** of retry logic

### Result

- Factory just assembles everything together
- `main.py` unchanged
  - still just calls `sensor.get_temperature()`
- Adding a new sensor is **easy**, just add to the list

---

## Why Retry and Fallback are Separate Decorators

- Retry and Fallback are **two different responsibilities**

- `RetryDecorator` only checks for reading from a sensor up to **N** times
- `FallbackDecorator` only moves to next sensor in the list
- If combined, would lead to multitasking which violates SRP

---

## How the Architecture Changed

### Before

- Retry logic lived inside each adapter in `adapters.py`
- Fallback logic lived inside the factory as `FallbackTemperatureSensor`

### After

- Adapters only read hardware, **LESS** logic
- `RetryDecorator` wraps any sensor and handles retries
- `FallbackDecorator` wraps a list of sensors and handles fallback
- Factory **only** assembles

---

## How SRP is Satisfied

- `DHTAdapter` / `ADSAdapter` : **read hardware**
- `RetryDecorator` : **retry on failure**
- `FallbackDecorator` : **try next sensor on failure**
- `SensorFactory` : **assemble the object**
- `main.py` : **read and print temperature**

---

## Diagrams

Please refer to Diagrams folder as some are too large to put in this `README.md` file. The diagrams consist of:

- Activity Diagram
- Class Diagram
- Sequence Diagram
- State Diagram
- Usecase Diagram
