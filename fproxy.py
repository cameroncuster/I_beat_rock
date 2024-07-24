import requests
from http.server import BaseHTTPRequestHandler, HTTPServer


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)

        url = f"https://www.whatbeatsrock.com{self.path}"
        headers = {
            "Cookie": self.headers.get("Cookie"),
            "User-Agent": "Cameron's Proxy Server",
        }

        try:
            response = requests.post(url, headers=headers, data=post_data, timeout=25)

            print(f"Received response from {url}")
            print(f"Response code: {response.status_code}")
            print(f"Response content: {response.content}")

            self.send_response(response.status_code)
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.end_headers()

            self.wfile.write(response.content)
            self.wfile.flush()
        except requests.RequestException as e:
            self.send_error(500, str(e))

        print(f"Completed request to {url}")


def run(server_class=HTTPServer, handler_class=ProxyHTTPRequestHandler, port=8080):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting proxy on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
