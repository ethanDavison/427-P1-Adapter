```mermaid
flowchart TD

start([Program Start])
A1[/"Load config, create sensor via SensorFactory"/]
A2[/"Read Primary Sensor (RetryDecorator)"/]
D1{Valid reading?}
S1[/"Append to buffer, apply Filter Strategy"/]
A4[/"Read Fallback Sensor (RetryDecorator)"/]
D2{Valid reading?}
S2[/"Append to buffer, apply Filter Strategy"/]
A3[/"Convert Temperature Celsius to Fahrenheit"/]
A5[/"Display Temperature"/]
stop([Program Termination])

start --> A1
A1 --> A2
A2 --> D1
D1 -- Yes --> S1
D1 -- No --> A4
S1 --> A3
A4 --> D2
D2 -- Yes --> S2
D2 -- No --> A2
S2 --> A3
A3 --> A5
A5 --> A2
A5 -. Program Stop .-> stop
```
