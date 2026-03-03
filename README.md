# 427 Project 1 - Hardware Abstraction with Adapter, Factory, and Decorator Patterns

## System Overview

This system takes the temperature reading from either a digital temperature sensor or an analog temperature sensor, or both, and displays a single syncronized result.

- This solves the problem that multiple sensors create, as two different results needs to be translated differently, but this system can read both.
- Supported sensors include: ADS1110, DHT11.
- The client of the system is whomever receives the synced temperature reading from the adapter pattern.

The design uses many patterns:
- An adapter pattern, to check for inputs from each type of sensor in case one is attached instead of the other,
- A factory pattern, with a configuration file that selects the prefered sensor and creates a single sensor object to encase it, and
- A decorator pattern, to add a Retry decoration (if get_temperature fails, it will retry a select amount of times), and a list-based Fallback decorator (when one sensor fails, it will go other sensors available in the list).

## UML Diagrams

### Use Case Diagram

![](Diagrams/useCaseDiagram.png)

### Activity Diagram

![](Diagrams/activityDiagram.png)

### Sequence Diagram

![](Diagrams/sequenceDiagram.png)

### Class Diagram

![](Diagrams/classDiagram.png)

### State Diagram

![](Diagrams/stateDiagram.png)
