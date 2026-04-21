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

## Adapter + Factory + Decorator + Observer

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
  - separation of concerns
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

## How the Architecture Changed (Decorator)

### Before

- Retry logic lived inside each adapter in `adapters.py`
- Fallback logic lived inside the factory as `FallbackTemperatureSensor`

### After

- Adapters only read hardware, **LESS** logic
- `RetryDecorator` wraps any sensor and handles retries
- `FallbackDecorator` wraps a list of sensors and handles fallback
- Factory **only** assembles

---

## How SRP is Satisfied (Decorator Phase)

- `DHTAdapter` / `ADSAdapter` : **read hardware**
- `RetryDecorator` : **retry on failure**
- `FallbackDecorator` : **try next sensor on failure**
- `SensorFactory` : **assemble the object**
- `main.py` : **read and print temperature**

---

## Observer Pattern - Why

### The problem after Decorator

- The sensor system works well **on a single device**
- But temperature data is locked inside the Pi
  - nothing else can receive or display it
- A single process cannot serve multiple consumers without tight coupling

### What we need

- A way to **broadcast** data to any number of receivers
- Receivers should be **independent** — adding one should not change anything else
- The Pi should not know or care **who** is listening

---

## Observer Pattern - What it is

### Core idea

- One **Subject** holds a list of **Observers**
- When new data arrives, the Subject calls `update(data)` on every Observer
- The Subject depends only on the **ObserverInterface**, not on any specific Observer class

### Why this fits our problem

- The Brain (Subject) can push readings to any number of consumers
- Adding a new consumer (logger, database, second dashboard) requires **zero changes** to the Brain
- The Pi only knows about the Brain — it never knows who is ultimately receiving the data

---

## Observer Pattern - Implementation

### Components

- `ObserverInterface` : base class with `update(data: dict)`
- `Brain` : the Subject — holds `_observers` list, implements `attach`, `detach`, `notify`
- `SocketObserver` : a concrete Observer — wraps a TCP socket and forwards data over the network
- `WebObserverClient` : connects to the Brain, receives pushed updates, stores latest readings

### The key design decision

- Observers **exist as external processes** (Docker containers), not in-memory objects
- The Brain wraps each incoming observer connection in a `SocketObserver`
- This maps the network-level connection to the Observer pattern interface

---

## How the Distributed Observer Works

### Two ports, two roles

- **Port 5000** — Pi producers connect here and send temperature readings
- **Port 5001** — Observers connect here and receive pushed updates

### Connection flow

1. Web container connects to Brain on port 5001
2. Brain wraps the socket in `SocketObserver` and calls `attach(observer)`
3. Pi sends a JSON reading to Brain on port 5000
4. Brain calls `notify(data)` which loops through `_observers` and calls `update(data)` on each
5. `SocketObserver.update` sends the JSON over the socket to the Web container
6. Web container receives the line, updates its `latest_data` dict, and the dashboard reflects the new reading

---

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
- A slow or dead observer does not block `notify` — the exception is caught and the observer is removed

---

## Fault Tolerance

### What the system handles

- **Malformed JSON from Pi** : caught with `json.JSONDecodeError`, message discarded, Pi connection stays open
- **Pi disconnects** : `_handle_pi` exits its loop cleanly when the socket closes
- **Observer disconnects** : `SocketObserver.update` raises on a broken socket; `notify` catches this, marks the observer dead, and removes it after the loop
- **Web container restarts** : it reconnects to Brain on port 5001 with a retry loop — the Brain is unaffected and simply gets a new `attach` call

---

## How Decoupling is Maintained

### Pi → Brain

- Pi only knows the Brain's IP and port
- Pi sends a JSON DTO and immediately closes the connection
- Pi has no knowledge of the Web container or any observer

### Brain → Observers

- Brain depends only on `ObserverInterface.update(data)`
- Brain does not import or reference `WebObserverClient`
- To add a new observer type (e.g. a database logger), create a new container that connects on port 5001 — no changes to `brain.py`

### Open/Closed Principle satisfied

- Brain is **closed** for modification
- The system is **open** for extension by adding new observer containers

---

## Full SRP Summary (All Phases)

- `DHTAdapter` / `ADSAdapter` : **read hardware**
- `RetryDecorator` : **retry on failure**
- `FallbackDecorator` : **try next sensor on failure**
- `SensorFactory` : **assemble the sensor stack**
- `main.py` (Pi) : **read sensor and send to Brain**
- `ObserverInterface` : **define the observer contract**
- `Brain` : **receive data and distribute to observers**
- `SocketObserver` : **forward data over a network socket**
- `WebObserverClient` : **receive updates and store latest readings**
- `DashboardHandler` : **serve the HTTP dashboard**

---

## Diagrams

Please refer to the Diagrams folder as some are too large to put in this file. The diagrams consist of:

- Activity Diagram — shows full flow from sensor read to dashboard update
- Class Diagram — includes all sensor, decorator, and observer classes
- Sequence Diagram — shows Observer registration and full data push flow
- State Diagram — Pi reading loop, Brain subject states, and Web observer states
- Use Case Diagram — all three actors (Pi, Brain, Web) and their responsibilities
