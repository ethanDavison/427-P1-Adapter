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

  h1, h2, h3, h4, h5, h6 {
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

## Adapter + Factory + Decorator + **Strategy**

**Using DHT11 and ADS sensors to read temperature from a Raspberry Pi**

---

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

---

<!-- _class: tinytext -->

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

---

<!-- _class: tinytext -->

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

---

## Design Constraints

- **Non-breaking** - `DHTAdapter` and `ADSAdapter` are not modified; they still return raw data
- **No throttling** - `sleep()` calls removed; `SmartSensor` is fast and non-blocking
- **Composition** - `SensorFactory` injects the `FilterStrategy` into `SmartSensor` at creation time
- **Interface stability** - `SmartSensor` implements `get_temperature()`, so nothing upstream changes

---

## Architectural Flow

1. `SensorFactory` creates the physical sensor and its adapter
2. Factory wraps the adapter in `SmartSensor` and injects a `MedianFilter`
3. Factory wraps `SmartSensor` in `FallbackDecorator`
4. `main.py` calls `get_temperature()` on the top-level decorator
5. `SmartSensor` pulls a raw sample, updates the sliding window buffer, returns the filtered result

---

## Diagrams

Please refer to the Diagrams folder as some are too large to include here. The diagrams consist of:

- Activity Diagram
- Class Diagram
- Sequence Diagram
- State Diagram
- Usecase Diagram
