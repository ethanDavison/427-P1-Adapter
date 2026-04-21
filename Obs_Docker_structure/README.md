# Obs_Docker_structure

## Folder structure

```
Obs_Docker_structure/
├── docker-compose.yml
├── README.md
├── brain/
│   ├── Dockerfile
│   ├── brain.py
│   └── observer_interface.py
└── web/
    ├── Dockerfile
    └── web_observer.py
```

## What is happening

The Pi sends temperature data over a raw TCP socket to the Brain on port 5000.
The Brain receives the data, parses the JSON, and pushes it to all registered
observers on port 5001. The Web Dashboard connects to the Brain on port 5001,
receives the pushed updates, and displays the latest reading from each Pi in a
table that auto-refreshes every 3 seconds.

### Brain container

- Runs two TCP servers simultaneously using two threads: port 5000 for Pi producers, port 5001 for observers
- Each Pi connection gets its own thread via `threading.Thread` so multiple Pis never block each other
- Any process connecting on port 5001 is automatically wrapped in a `SocketObserver` and attached to the Brain's observer list via `attach(observer)`
- When `notify(data)` is called, it iterates the observer list and calls `observer.update(data)` on each one, sending the JSON over that observer's socket
- If an observer disconnects mid-send, the exception is caught and the dead observer is removed from the list - the Brain keeps running

### Web container

- Connects to the Brain on port 5001 and blocks reading line-delimited JSON
- Uses `socket.makefile` to read line by line so partial TCP packets are handled correctly
- Stores the latest reading per Pi ID in a `latest_data` dict
- Runs a minimal `HTTPServer` on port 8080 in a separate thread at the same time as the socket listener
- The dashboard HTML includes `<meta http-equiv="refresh" content="3">` so the browser polls for updates every 3 seconds without any JavaScript required

## Docker

Running `docker-compose up --build` builds an image for each service. The Brain
and Web Dashboard each get their own image which Docker runs as containers on
the same internal bridge network (`iot-net`), allowing them to communicate using
the service name `brain` instead of an IP address.

- Brain exposes port 5000 (Pi connections) and port 5001 (observer connections)
- Web exposes port 8080 (dashboard, open in browser at `http://localhost:8080`)
- Services communicate using the container name `brain` - this is why `web_observer.py` sets `BRAIN_HOST = "brain"`

## Running

Edit `config.json` on each Pi so that `brain_host` is the **local IPv4 address**
of the machine running Docker (not `localhost` - the Pi is on a different device).

Then run the following command **inside the `Obs_Docker_structure` folder**:

```
docker-compose up --build
```

Start each Pi script after the containers are up:

```
python main.py
```

To simulate a second Pi without hardware, run `fake_pi.py` from any machine on
the same network, updating `BRAIN_HOST` to match.

## Config examples

DHT11 primary sensor:

```json
{
  "mode": "dht11",
  "pin": 21,
  "chip": 0,
  "pi_id": "Pi_A",
  "brain_host": "10.36.224.120",
  "brain_port": 5000
}
```

ADS primary sensor:

```json
{
  "mode": "ads",
  "lm_type": "LM35",
  "pi_id": "Pi_B",
  "brain_host": "10.36.224.120",
  "brain_port": 5000
}
```

> `brain_host` must be the IPv4 address of the machine running Docker, not `localhost`.

## Network note - real Pi vs simulated Pi

When receiving data from a **real Raspberry Pi connected via Ethernet**, the `brain_host` in `config.json` must be the **Ethernet IPv4 address** of the machine running Docker (e.g. the address assigned to your `eth0` interface), not the Wi-Fi address. The Pi is on the Ethernet network so it can only reach the host through that interface - using the Wi-Fi address will cause the connection to fail or time out.

For any **simulated Pi scripts** (e.g. `simulate_pi.py`) running on a laptop or desktop on the same Wi-Fi network, the regular Wi-Fi IPv4 address works fine. use the `ipconfig` command to find these via command line.
