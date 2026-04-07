import socket
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

BRAIN_HOST = "brain"
BRAIN_PORT = 5001

latest_data = {}

def listen_to_brain():
    time.sleep(3)
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((BRAIN_HOST, BRAIN_PORT))
                # Treat socket as a file to read line by line
                f = s.makefile('r', encoding='utf-8')
                for line in f:
                    if not line:
                        break
                    parsed = json.loads(line.strip())
                    latest_data[parsed["origin"]] = parsed
        except Exception as e:
            print(f"Retrying... {e}")
            time.sleep(2)

# build a simple tabble to display our data
class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        rows = ""
        for pi_id, reading in latest_data.items():
            temp = reading["payload"]["temp"]
            unit = reading["payload"]["unit"]
            timestamp = reading["timestamp"]
            rows += f"<tr><td>{pi_id}</td><td>{temp} {unit}</td><td>{timestamp}</td></tr>"

        html = f"""
        <html>
        <head>
            <title>Pi Temp Dashboard</title>
            <meta http-equiv="refresh" content="3">
        </head>
        <body>
            <h2>Raspberry Pi Temp Readings</h2>
            <table border="1" cellpadding="8">
                <tr><th>Pi ID</th><th>Temperature</th><th>Timestamp</th></tr>
                {rows}
            </table>
        </body>
        </html>"""

        # HTTP protocal needs status line, headers, blank line and body
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    # thread so that the HTTP sever and lising to brain func happen at same time
    threading.Thread(target=listen_to_brain, daemon=True).start()
    print("Dashboard running on http://localhost:8080")
    HTTPServer(("0.0.0.0", 8080), DashboardHandler).serve_forever()