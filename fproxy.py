import requests
from http.server import BaseHTTPRequestHandler, HTTPServer


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # assume the path is correct
        url = f"https://www.whatbeatsrock.com/api{self.path}"

        cookie = self.headers["Cookie"]

        headers = {
            "Cookie": cookie,
            "User-Agent": "Cameron's Proxy Server",
        }

        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)

        response = requests.post(url, headers=headers, data=post_data)

        self.send_response(response.status_code)
        for key, value in response.headers.items():
            self.send_header(key, value)
        self.end_headers()

        self.wfile.write(response.content)


def run(server_class=HTTPServer, handler_class=ProxyHTTPRequestHandler, port=8080):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting proxy on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
