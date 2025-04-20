import ipaddress
from wsgiref.simple_server import WSGIRequestHandler, make_server

from prometheus_client import REGISTRY, generate_latest

ALLOWED_NET_V4 = ipaddress.ip_network("10.0.0.0/8")
ALLOWED_LOCAL_V4 = ipaddress.ip_network("127.0.0.0/8")
ALLOWED_LOCAL_V6 = ipaddress.ip_network("::1/128")


def metrics_app(environ, start_response):
    client_ip_raw = environ.get("REMOTE_ADDR", "")
    client_ip = ipaddress.ip_address(client_ip_raw)

    if (
        client_ip not in ALLOWED_NET_V4
        and client_ip not in ALLOWED_LOCAL_V4
        and client_ip not in ALLOWED_LOCAL_V6
    ):
        start_response("403 Forbidden", [("Content-Type", "text/plain")])
        return [b"Forbidden"]

    if environ["PATH_INFO"] != "/metrics":
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Not Found"]

    output = generate_latest(REGISTRY)
    start_response("200 OK", [("Content-Type", "text/plain; version=0.0.4")])
    return [output]


def start_metrics_server(port=8001):
    class QuietHandler(WSGIRequestHandler):
        def log_message(self, *args, **kwargs):
            pass

    print(f"✅ Serving Prometheus metrics on http://0.0.0.0:{port}/metrics")
    httpd = make_server("0.0.0.0", port, metrics_app, handler_class=QuietHandler)
    httpd.serve_forever()
