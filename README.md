---
marp: true
theme: default
paginate: true
mermaid: true
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

## Adapter → Factory

**Using DHT11 and ADS sensors to read temperature from a Raspberry Pi**

---

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

---

## The Problem — Tight Coupling in main.py

**main knew WAY too much:**

- Imports concrete hardware classes directly
- Knows constructor arguments
- Manages hardware initialization
- Adding a third sensor = **modifying main**

The main application layer should not know concrete implementations.

---

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

---

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

---

## Diagrams

Please refer to Diagrams folder as some are too large to put in this `README.md` file. The diagrams consist of:

- Activity Diagram
- Class Diagram
- Sequence Diagram
- State Diagram
- Usercase Diagram
