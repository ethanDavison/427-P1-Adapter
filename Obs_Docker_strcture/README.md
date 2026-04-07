# This is the folder structure you would use for Docker

## Basically what's happening

The Pi sends temperature data over a raw TCP socket to the Brain on port 5000.
The Brain receives the data, parses the JSON, and pushes it to all registered
observers on port 5001. The Web Dashboard connects to the Brain on port 5001,
receives the pushed updates, and displays the latest reading from each Pi in a
table that auto refreshes every 3 seconds.

- Brain runs two TCP servers simultaneously : port 5000 for Pi producers, port 5001 for observers
- Any process connecting on port 5001 is wrapped in a `SocketObserver` and registered automatically
- Each Pi connection gets its own thread so multiple Pis never block each other
- If an observer disconnects, it is automatically removed from the observer list on the next `notify()`
- The Web Dashboard runs the socket listener and HTTP server on separate threads at the same time

## Docker

Running `docker-compose up --build` builds an image for each service. The Brain
and Web Dashboard each get their own image which Docker then runs as containers
on the same internal network, allowing them to communicate using the service
name `brain` instead of an IP address.

- Brain exposes port 5000 (Pi connections) and port 5001 (observer connections)
- Web exposes port 8080 (dashboard)
- Services communicate using the container name `brain` instead of localhost

## Running

Edit config files on Pi to have the `IPv4` address of the machine running Docker
and run the command below in the same **directory as this folder**

```
docker-compose up --build
```
