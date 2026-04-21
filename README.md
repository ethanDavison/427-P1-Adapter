# 427 Project - Designing Temperature Sensors

This project is the semester-long work of Xavier S. and Ethan D. for Montana Tech's <i>CSCI 427 Software Design and Architecture</i> class! It includes the use of multiple software design patterns that progressively lead into one another, starting with:

- The Adapter Pattern: 
    - Solved the problem of using multiple sensors and needing to translate their outputs differently.
    - Using two sensors that provided seperate outputs (the ADS1110 and DHT11 sensors, specifically), the outputs for either were checked, and a single result was chosen and given.
- The Factory Pattern:
    - Solved the problem of tight coupling made by hardcoding primary logic and functions into the `main()` function.
    - Using a config file and object creation, responsibility is separated from `main.py` and temperature sensing logic can be completely seperate from the `main()` function!
- The Decorator Pattern:
    - Solved the problem of needing to nest multiple logical jobs within the factory and adapter classes.
    - By using multple decorators, existing sensor objects can be given new behavior without modifying the now simplified code.
- The Strategy Pattern:
    - Solved the problem of repeatedly checking noisy data for failed readings every time the sensor is run.
    - By averaging multiple readings of a sensor's raw temperature data, failed readings no longer need to be checked conditionally for each individual reading.
- The Observer Pattern:
    - Solved the problem of needing to run the entire system on one device.
    - Data from the `main()` function (the Brain) is now broadcasted out from the device and can be recieved independently from any desired observers!

More details are provided below in the segments taken from each pattern branch's README.md files!


# Pattern 1: Adapter Pattern

## System Overview

This system takes the temperature reading from either a digital temperature sensor or an analog temperature sensor, or both, and displays a single syncronized result.

- This solves the problem that multiple sensors create, as two different results needs to be translated differently, but this system can read both.
- Supported sensors include: ADS1110, DHT11.
- The design uses an adapter pattern to check for inputs from each type of sensor in case one is attached instead of the other. It also can swap to a secondary sensor in the case that one malfunctions.
- The client of the system is whomever receives the synced temperature reading from the adapter pattern.



# Pattern 2: Factory Pattern 

## Previous Project — Adapter Pattern

### Problem

`main.py` called two completely different sensor libraries directly

### What We Did

- Created `adapters.py`, and adapter classes for both `DHT11` and `ANDS`
- Baked in retry logic in both adapter classes
- Both implement `get_temperature()` from a shared `TemperatureSensor` base class

### Result

- created instances of both sensors, and added them to a list

- `main.py` only called `sensor.get_temperature()` on a instance in a list

## The Problem — Tight Coupling in main.py

**main knew WAY too much:**

- Imports concrete hardware classes directly
- Knows constructor arguments
- Manages hardware initialization
- Adding a third sensor = **modifying main**

The main application layer should not know concrete implementations.

## Solution — Simple Factory Pattern

**Refactor object creation out of main entirely:**

- **Isolate** object creation logic into one place
- **Remove** direct knowledge of concrete classes from main
- **Read** Config file
- **Improve** separation of responsibilities
- **Prepare** the system for future extensions

```python
# main.py
from sensor_factory import SensorFactory

# load our config and sensor from config
config = load_config()
sensor = SensorFactory.create_sensor(config)
```

One import. No hardware knowledge. No constructor arguments.

## Why Object Creation is a Separate Responsibility

**Creation logic changes for different reasons than application logic.**

- Adding a new sensor = factory changes, main **doesn't**
- Changing hardware init = factory changes, main **doesn't**
- Swapping libraries = factory changes, main **doesn't**

**Advantages of isolating hardware creation:**

- One place to update when hardware changes
- main is testable without real hardware
- Factory can be swapped without touching application code
- Future sensors added with zero impact on main

If main creates objects, it owns the risk of every hardware change.


# Pattern 3: Decorator Pattern 

## Previous Project - Adapter & Simple Factory Summary

### Adapter Pattern

- `DHTAdapter` and `ADSAdapter` both implement `get_temperature()` via the shared `TemperatureSensor` base class
- Each adapter retries up to 3 times before returning `None`
- `main.py` talks to either sensor the same way

### Simple Factory

- `SensorFactory.create_sensor(config)` reads `config.json` and wraps two sensors in `FallbackTemperatureSensor`
  - if primary returns `None`, it tries secondary sensor for redundancy
- `main.py` only imports `SensorFactory`

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

## Why Retry and Fallback are Separate Decorators

- Retry and Fallback are **two different responsibilities**

- `RetryDecorator` only checks for reading from a sensor up to **N** times
- `FallbackDecorator` only moves to next sensor in the list
- If combined, would lead to multitasking which violates SRP

## How the Architecture Changed

### Before

- Retry logic lived inside each adapter in `adapters.py`
- Fallback logic lived inside the factory as `FallbackTemperatureSensor`

### After

- Adapters only read hardware, **LESS** logic
- `RetryDecorator` wraps any sensor and handles retries
- `FallbackDecorator` wraps a list of sensors and handles fallback
- Factory **only** assembles

## How SRP is Satisfied

- `DHTAdapter` / `ADSAdapter` : **read hardware**
- `RetryDecorator` : **retry on failure**
- `FallbackDecorator` : **try next sensor on failure**
- `SensorFactory` : **assemble the object**
- `main.py` : **read and print temperature**


# Pattern 4: Strategy Pattern

## The Problem - Raw Data is Noisy

> _"The goal of this phase is to move from 'raw data reading' to 'signal processing.'"_

- A single hardware reading can be wrong - noise, interference, sensor lag
- Calling `get_temperature()` directly returns **one raw sample**
- The result is jittery and unreliable output
- `sleep()` is a workaround, not a fix - it slows the system without filtering bad data

### What we actually need

- Collect **multiple samples** over time into a buffer
- Apply a **filter** to produce a stable, meaningful value
- Keep the filtering logic **swappable** - different situations call for different strategies

## The Solution - SmartSensor + Strategy Pattern

### SmartSensor

A new wrapper that sits **above the adapter layer**:

- Wraps any object implementing `get_temperature()` - no existing code modified
- Maintains a **sliding window buffer** - default 10 samples, FIFO
- Records the **timestamp** of each measurement to ensure correct sampling frequency
- Implements `get_temperature()` itself - fully compatible with existing decorators and fallback

### Strategy Pattern

- A `FilterStrategy` interface decouples **filtering logic** from **sensor logic**
- `SmartSensor` delegates all math to whichever strategy is injected into it
- `SensorFactory` injects the chosen `FilterStrategy` at creation time - composition over hardcoding

## FilterStrategy - Three Implementations

| Strategy        | Logic                                   | Use Case                       |
| --------------- | --------------------------------------- | ------------------------------ |
| `MeanFilter`    | Arithmetic average of the buffer        | General smoothing of noise     |
| `MedianFilter`  | Sort buffer, return the middle value    | Removing spikes and outliers   |
| `RawPassFilter` | Return the most recent sample unchanged | Debugging or low-latency needs |

### Why this is the Strategy Pattern

- All three implement the same `FilterStrategy` interface
- `SmartSensor` doesn't know or care which one it holds
- Swapping the filter **does not change** `SmartSensor`, the adapters, or `main.py`

## Design Constraints

- **Non-breaking** - `DHTAdapter` and `ADSAdapter` are not modified; they still return raw data
- **No throttling** - `sleep()` calls removed; `SmartSensor` is fast and non-blocking
- **Composition** - `SensorFactory` injects the `FilterStrategy` into `SmartSensor` at creation time
- **Interface stability** - `SmartSensor` implements `get_temperature()`, so nothing upstream changes

## Architectural Flow

1. `SensorFactory` creates the physical sensor and its adapter
2. Factory wraps the adapter in `SmartSensor` and injects a `MedianFilter`
3. Factory wraps `SmartSensor` in `FallbackDecorator`
4. `main.py` calls `get_temperature()` on the top-level decorator
5. `SmartSensor` pulls a raw sample, updates the sliding window buffer, returns the filtered result


# Pattern 5: Observer Pattern

## Observer Pattern - Why

### The problem after Strategy

- The sensor system works well **on a single device**
- But temperature data is locked inside the Pi
  - nothing else can receive or display it
- A single process cannot serve multiple consumers without tight coupling

### What we need

- A way to **broadcast** data to any number of receivers
- Receivers should be **independent** - adding one should not change anything else
- The Pi should not know or care **who** is listening

## Observer Pattern - What it is

### Core idea

- One **Subject** holds a list of **Observers**
- When new data arrives, the Subject calls `update(data)` on every Observer
- The Subject depends only on the **ObserverInterface**, not on any specific Observer class

### Why this fits our problem

- The Brain (Subject) can push readings to any number of consumers
- Adding a new consumer (logger, database, second dashboard) requires **zero changes** to the Brain
- The Pi only knows about the Brain - it never knows who is ultimately receiving the data

## Observer Pattern - Implementation

### Components

- `ObserverInterface` : base class with `update(data: dict)`
- `Brain` : the Subject - holds `_observers` list, implements `attach`, `detach`, `notify`
- `SocketObserver` : a concrete Observer - wraps a TCP socket and forwards data over the network
- `WebObserverClient` : connects to the Brain, receives pushed updates, stores latest readings

### The key design decision

- Observers **exist as external processes** (Docker containers), not in-memory objects
- The Brain wraps each incoming observer connection in a `SocketObserver`
- This maps the network-level connection to the Observer pattern interface

## How the Distributed Observer Works

### Two ports, two roles

- **Port 5000** - Pi producers connect here and send temperature readings
- **Port 5001** - Observers connect here and receive pushed updates

## Connection flow

1. Web container connects to Brain on port 5001
2. Brain wraps the socket in `SocketObserver` and calls `attach(observer)`
3. Pi sends a JSON reading to Brain on port 5000
4. Brain calls `notify(data)` which loops through `_observers` and calls `update(data)` on each
5. `SocketObserver.update` sends the JSON over the socket to the Web container
6. Web container receives the line, updates its `latest_data` dict, and the dashboard reflects the new reading

## Concurrency - How Multiple Clients Are Handled

### The problem

- Multiple Pis connecting at the same time would block each other on a single thread
- The Brain must also handle observer connections at the same time as Pi connections

### Solution: threading

- `start_pi_server` spawns a **new daemon thread** for each Pi connection via `threading.Thread`
- `start_observer_server` runs in the main thread; Pi server runs in a background thread
- A `threading.Lock` protects `_observers` so concurrent `notify` and `attach` calls do not corrupt the list

### Result

- A slow Pi does not block other Pis
- A slow or dead observer does not block `notify` - the exception is caught and the observer is removed

## Fault Tolerance

### What the system handles

- **Malformed JSON from Pi** : caught with `json.JSONDecodeError`, message discarded, Pi connection stays open
- **Pi disconnects** : `_handle_pi` exits its loop cleanly when the socket closes
- **Observer disconnects** : `SocketObserver.update` raises on a broken socket; `notify` catches this, marks the observer dead, and removes it after the loop
- **Web container restarts** : it reconnects to Brain on port 5001 with a retry loop - the Brain is unaffected and simply gets a new `attach` call

## How Decoupling is Maintained

### Pi → Brain

- Pi only knows the Brain's IP and port
- Pi sends a JSON DTO and immediately closes the connection
- Pi has no knowledge of the Web container or any observer

### Brain → Observers

- Brain depends only on `ObserverInterface.update(data)`
- Brain does not import or reference `WebObserverClient`
- To add a new observer type (e.g. a database logger), create a new container that connects on port 5001 - no changes to `brain.py`

### Open/Closed Principle satisfied

- Brain is **closed** for modification
- The system is **open** for extension by adding new observer containers