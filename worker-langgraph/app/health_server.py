from http.server import BaseHTTPRequestHandler, HTTPServer


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")


def run():
    server = HTTPServer(("", 10000), HealthHandler)
    print("Health server running on port 10000")
    server.serve_forever()


if __name__ == "__main__":
    run()
