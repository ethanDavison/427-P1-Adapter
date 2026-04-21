import socket
import threading
import json
from observer_interface import ObserverInterface

# The Subject in the Observer pattern
class Brain:
    def __init__(self):
        # list of all registered observers
        self._observers = []
        self._lock = threading.Lock()

    # add an observer to the list
    def attach(self, observer: ObserverInterface):
        with self._lock:
            self._observers.append(observer)

    # remove an observer from the list
    def detach(self, observer: ObserverInterface):
        with self._lock:
            self._observers.remove(observer)

    # push data to all registered observers
    def notify(self, data: dict):
        with self._lock:
            dead = []
            for observer in self._observers:
                try:
                    observer.update(data)
                except Exception:
                    dead.append(observer)
            for d in dead:
                self._observers.remove(d)

    # listen for incoming Pi connections on port 5000
    def start_pi_server(self, port=5000):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", port))
        server.listen()
        while True:
            # each Pi gets its own thread so we dont block
            conn, addr = server.accept()
            threading.Thread(target=self._handle_pi, args=(conn,), daemon=True).start()

    # listen for incoming observer connections on port 5001
    def start_observer_server(self, port=5001):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", port))
        server.listen()
        while True:
            # each observer gets its own thread
            conn, addr = server.accept()
            observer = SocketObserver(conn)
            self.attach(observer)

    # handle a single Pi connection, parse the JSON and notify observers
    def _handle_pi(self, conn):
        with conn:
            # Use makefile to treat the socket like a file with lines
            f = conn.makefile('r', encoding='utf-8')
            for line in f:
                if not line:
                    break
                try:
                    parsed = json.loads(line.strip())
                    self.notify(parsed)
                except json.JSONDecodeError:
                    print("Failed to parse incoming data")


# a socket based observer that the Brain pushes data to
class SocketObserver(ObserverInterface):
    def __init__(self, conn):
        self._conn = conn

    def update(self, data: dict):
        try:
            # Add a newline so the receiver knows the message ended
            message = json.dumps(data) + "\n"
            self._conn.sendall(message.encode())
        except Exception as e:
            print(f"error: {e}")
            raise e # Let notify() catch this to remove the dead observer


if __name__ == "__main__":
    brain = Brain()
    # start Pi listener in background thread
    threading.Thread(target=brain.start_pi_server, daemon=True).start()
    # start observer listener in main thread
    brain.start_observer_server()