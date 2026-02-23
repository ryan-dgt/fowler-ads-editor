from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

port = int(os.environ.get("PORT", 8080))

handler = SimpleHTTPRequestHandler
httpd = HTTPServer(("0.0.0.0", port), handler)
print(f"Serving on port {port}")
httpd.serve_forever()
