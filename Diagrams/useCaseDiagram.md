```mermaid
flowchart TD
    USER(("**fa:fa-user** User"))

    subgraph SYS["Rasp Pi Temp Monitoring Sys"]
        UC1[/"Read Temperature"/]
        UC2[/"Auto Select Sensor"/]
        UC3[/"Display Temperature"/]
        UC4[/"Load Config"/]
    end
    UC0[/"Start Measurement"/]
    UC5[/"Stop Measurement"/]

    USER --> UC0
    UC0 --> SYS
    UC4 --> SYS
    SYS --> UC1
    UC1 --> UC2
    UC2 --> UC3
    USER --> UC5
```
