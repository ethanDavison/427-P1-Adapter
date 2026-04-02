# This is the folder structure you would use for Docker

## Basically wahts happening

The Pi sends temperature data over a raw TCP socket to the Brain on port 5000.
The Brain receives the data, parses the JSON, and pushes it to all registered
observers on port 5001. The Web Dashboard connects to the Brain on port 5001,
receives the pushed updates, and displays the latest reading from each Pi in a
table that auto refreshes every 3 seconds.

## Docker

Running `docker-compose up --build` builds an image for each service. The Brain and Web Dashboard each get their own image which Docker then runs as
containers on the same internal network, allowing them to communicate using the
service name `brain` instead of an IP address.

## Running

Edit Config files on pi to have the `Ipv4` addess of machine that is running docker and run the command below in the same **directory as this folder**

```
docker-compose up --build
```
