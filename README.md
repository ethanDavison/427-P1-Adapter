---
marp: true
theme: default
paginate: true
footer: "Software Architecture Presentations - Object Creation & Access Control"
style: |
  @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap");

  :root {
  font-family: "Work Sans Regular", Arial;
  --main-color: #2c3e50;
  --text-color: #2c3e50;
  --bg-color-alt: #ffffff;
  --mark-background: #aed6f1;
  }

  section {
  background-color: #ffffff;
  background-size: 20px 20px;
  background-image:
    linear-gradient(#2c3e5012 1px, transparent 1px),
    linear-gradient(to right, #2c3e5012 1px, #2c3e500a 1px);
  }

  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    color: var(--text-color);
  }

  header {
    font-size: 0.7em;
    color: var(--text-color);
    border-bottom: 1px solid #2c3e50;
  }

  footer {
    font-size: 0.7em;
    color: var(--text-color);
    border-top: 1px solid #2c3e50;
  }

  code {
    background-color: #d5d8dc;
    font-size: 0.9em;
  }

  pre {
    background-color: #d5d8dc;
  }

  blockquote {
    background: #d5d8dc;
    border-left: 10px solid var(--main-color);
    margin: 0.5em;
    padding: 0.5em;
  }

  mark {
    background-color: #5dade2;
    padding: 0 2px 2px;
  }

  section::after {
    font-size: 0.75em;
    content: attr(data-marpit-pagination) " / " attr(data-marpit-pagination-total);
    color: var(--text-color);
  }

  table {
    display: block;
    margin: 0 auto;
  }

  th {
    background-color: #34495e;
    color: white;
  }

  /* <!-- _class: tinytext --> */
  /* Makes p, ul, and blockquote text smaller to fit more text on a slide */
  section.tinytext > p,
  section.tinytext > ul,
  section.tinytext > blockquote {
    font-size: 0.65em;
  }

  img[alt~="center"] {
    display: block;
    margin: 0 auto;
  }
---

# Temperature Sensor System

## Adapter + Factory + Decorator + Strategy + Observer

**Using DHT11 and ADS sensors to read temperature from a Raspberry Pi**

---

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

---

 <!-- _class: tinytext -->

## Observer Pattern - What it is

### Core idea

- One **Subject** holds a list of **Observers**
- When new data arrives, the Subject calls `update(data)` on every Observer
- The Subject depends only on the **ObserverInterface**, not on any specific Observer class

### Why this fits our problem

- The Brain (Subject) can push readings to any number of consumers
- Adding a new consumer (logger, database, second dashboard) requires **zero changes** to the Brain
- The Pi only knows about the Brain - it never knows who is ultimately receiving the data

---

 <!-- _class: tinytext -->

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

---

## How the Distributed Observer Works

### Two ports, two roles

- **Port 5000** - Pi producers connect here and send temperature readings
- **Port 5001** - Observers connect here and receive pushed updates

---

## Connection flow

1. Web container connects to Brain on port 5001
2. Brain wraps the socket in `SocketObserver` and calls `attach(observer)`
3. Pi sends a JSON reading to Brain on port 5000
4. Brain calls `notify(data)` which loops through `_observers` and calls `update(data)` on each
5. `SocketObserver.update` sends the JSON over the socket to the Web container
6. Web container receives the line, updates its `latest_data` dict, and the dashboard reflects the new reading

---

<!-- _class: tinytext -->

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

---

## Fault Tolerance

### What the system handles

- **Malformed JSON from Pi** : caught with `json.JSONDecodeError`, message discarded, Pi connection stays open
- **Pi disconnects** : `_handle_pi` exits its loop cleanly when the socket closes
- **Observer disconnects** : `SocketObserver.update` raises on a broken socket; `notify` catches this, marks the observer dead, and removes it after the loop
- **Web container restarts** : it reconnects to Brain on port 5001 with a retry loop - the Brain is unaffected and simply gets a new `attach` call

---

 <!-- _class: tinytext -->

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

---

## Diagrams

Please refer to the Diagrams folder as some are too large to put in this file. The diagrams consist of:

- Activity Diagram - shows full flow from sensor read to dashboard update
- Class Diagram - includes all sensor, decorator, strategy, and observer classes
- Sequence Diagram - shows Observer registration and full data push flow
- State Diagram - Pi reading loop, Brain subject states, and Web observer states
- Use Case Diagram - all three actors (Pi, Brain, Web) and their responsibilities
