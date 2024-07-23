import json
import uuid
import requests


class GraniteGladiator:
    headers = {
        "Cookie": "sb-xrrlbpmfxuxumxqbccxz-auth-token=%5B%22eyJhbGciOiJIUzI1NiIsImtpZCI6IjB3Q3RxNnJ0NmpGSWs3TWEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3hycmxicG1meHV4dW14cWJjY3h6LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIwNGE4OWUzYi02NWI4LTRkZmMtYjRiZi0yODhhYmE5N2ExNjciLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzIxNzcwMjc1LCJpYXQiOjE3MjE3NjY2NzUsImVtYWlsIjoiY3VzdGVyLmNhbWVyb25AZ21haWwuY29tIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJnb29nbGUiLCJwcm92aWRlcnMiOlsiZ29vZ2xlIl19LCJ1c2VyX21ldGFkYXRhIjp7ImF2YXRhcl91cmwiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NMRjN6Uml6OHo1TzJkd2hRSjJUU3dOQmdaSUN5MjdJTWlldmdKdFFTZ0k1ZU5Mc1E9czk2LWMiLCJlbWFpbCI6ImN1c3Rlci5jYW1lcm9uQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmdWxsX25hbWUiOiJDYW1lcm9uIEN1c3RlciIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbSIsIm5hbWUiOiJDYW1lcm9uIEN1c3RlciIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0xGM3pSaXo4ejVPMmR3aFFKMlRTd05CZ1pJQ3kyN0lNaWV2Z0p0UVNnSTVlTkxzUT1zOTYtYyIsInByb3ZpZGVyX2lkIjoiMTE1MTU0MDI5MDk0Njc0MTg3ODM2Iiwic3ViIjoiMTE1MTU0MDI5MDk0Njc0MTg3ODM2In0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoib2F1dGgiLCJ0aW1lc3RhbXAiOjE3MjE3NjY2NzV9XSwic2Vzc2lvbl9pZCI6Ijk5NTI0ODZkLTE0ZDEtNGFhOC05NTgwLTdlNDNmNDdiYTZmYyIsImlzX2Fub255bW91cyI6ZmFsc2V9.ZCLCPll04Qmc6Ib-E0kNFD1vh9yfaipzACd31viUkxg%22%2C%22RKvgdJcVmUrTELdsJE6O_Q%22%2C%22ya29.a0AXooCgteTO14Js_0SKFS5c8g2wuR3-aqozmAf9lyX3bPZVVBTOU0v3e2MAIWhduL57qzw8bO9QaQo2ZqGkxTJOhlm6mAV0qcCZDNoer7f9eKtnTGc1E5-OaZJiVOJ3Yctw71XeMw2Nvhu1lf7xo7oVQQzjGzViQ_LqUZaCgYKATMSARISFQHGX2Miy_sxeQbehk8M-yXfDBn24Q0171%22%2C%221%2F%2F05V6Uh9jSsnYICgYIARAAGAUSNwF-L9IrV-ao76tEZMDAbf1ybmQSDJSooIQOg5Holbd1XeaNkop7Y6d6YOhBzR4n07dLnXqd3cE%22%2Cnull%5D",
        "User-Agent": "Cameron's Machine",
    }

    def __init__(self):
        self.log_file = open("guesses.txt", "w")
        self.gid = str(uuid.uuid4())
        self.prev = "rock"
        self.score = 0

    def __del__(self):
        self.log_file.close()

    def save_score(self, guess):
        print(f"score: {self.score}")

        data = {
            "gid": self.gid,
            "score": self.score,
            "text": f"{guess} 🧑 did not beat {self.prev} 🫦",
        }

        response = requests.post(
            "https://www.whatbeatsrock.com/api/scores", headers=self.headers, json=data
        )

        print(f"score saving status code: {response.status_code}")
        print(f"score saving text: {response.text}")

    def log_guess(self, guess):
        self.log_file.write(f"{guess}\n")

    def make_guess(self, guess):
        self.log_guess(guess)

        print(f"guess: {guess}")

        data = {"prev": self.prev, "guess": guess, "gid": self.gid}

        response = requests.post(
            "https://www.whatbeatsrock.com/api/vs", headers=self.headers, json=data
        )

        if response.status_code == 200:
            pretty_response_content = json.dumps(response.json(), indent=2)

            print(f"response content: {pretty_response_content}")

            if response.json().get("data").get("guess_wins"):
                self.score += 1
                self.prev = guess
                return True
            else:
                return False
        else:
            print(f"guess status code: {response.status_code}")
            print(f"guess error: {response.text}")
            return False


def int_to_base26(value):
    chars = "abcdefghijklmnopqrstuvwxyz"

    if value == 0:
        return chars[0]

    base26_str = ""
    base = len(chars)

    while value > 0:
        value, remainder = divmod(value, base)
        base26_str = chars[remainder] + base26_str

    return base26_str


player = GraniteGladiator()

player.make_guess("paper")
player.make_guess("scissors")

prv_name = 0
guess = ""

try:
    while True:
        cur_name = prv_name + 1
        guess = f"a God named '{int_to_base26(cur_name)}' who defeats a God named '{int_to_base26(prv_name)}'"
        if not player.make_guess(guess):
            break
        prv_name = cur_name
except KeyboardInterrupt:
    print("interrupted...")

player.save_score(guess)

