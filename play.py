import json
import uuid
import emoji
import string
import random
import requests

class GraniteGladiator:
    # Class Constants
    URL_PLAY = "https://www.whatbeatsrock.com/api/vs"
    URL_SCORES = "https://www.whatbeatsrock.com/api/scores"
    HEADERS = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Cookie": "sb-xrrlbpmfxuxumxqbccxz-auth-token=%5B%22eyJhbGciOiJIUzI1NiIsImtpZCI6IjB3Q3RxNnJ0NmpGSWs3TWEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3hycmxicG1meHV4dW14cWJjY3h6LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIwNGE4OWUzYi02NWI4LTRkZmMtYjRiZi0yODhhYmE5N2ExNjciLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzIxNzcwMjc1LCJpYXQiOjE3MjE3NjY2NzUsImVtYWlsIjoiY3VzdGVyLmNhbWVyb25AZ21haWwuY29tIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJnb29nbGUiLCJwcm92aWRlcnMiOlsiZ29vZ2xlIl19LCJ1c2VyX21ldGFkYXRhIjp7ImF2YXRhcl91cmwiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NMRjN6Uml6OHo1TzJkd2hRSjJUU3dOQmdaSUN5MjdJTWlldmdKdFFTZ0k1ZU5Mc1E9czk2LWMiLCJlbWFpbCI6ImN1c3Rlci5jYW1lcm9uQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmdWxsX25hbWUiOiJDYW1lcm9uIEN1c3RlciIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbSIsIm5hbWUiOiJDYW1lcm9uIEN1c3RlciIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0xGM3pSaXo4ejVPMmR3aFFKMlRTd05CZ1pJQ3kyN0lNaWV2Z0p0UVNnSTVlTkxzUT1zOTYtYyIsInByb3ZpZGVyX2lkIjoiMTE1MTU0MDI5MDk0Njc0MTg3ODM2Iiwic3ViIjoiMTE1MTU0MDI5MDk0Njc0MTg3ODM2In0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoib2F1dGgiLCJ0aW1lc3RhbXAiOjE3MjE3NjY2NzV9XSwic2Vzc2lvbl9pZCI6Ijk5NTI0ODZkLTE0ZDEtNGFhOC05NTgwLTdlNDNmNDdiYTZmYyIsImlzX2Fub255bW91cyI6ZmFsc2V9.ZCLCPll04Qmc6Ib-E0kNFD1vh9yfaipzACd31viUkxg%22%2C%22RKvgdJcVmUrTELdsJE6O_Q%22%2C%22ya29.a0AXooCgteTO14Js_0SKFS5c8g2wuR3-aqozmAf9lyX3bPZVVBTOU0v3e2MAIWhduL57qzw8bO9QaQo2ZqGkxTJOhlm6mAV0qcCZDNoer7f9eKtnTGc1E5-OaZJiVOJ3Yctw71XeMw2Nvhu1lf7xo7oVQQzjGzViQ_LqUZaCgYKATMSARISFQHGX2Miy_sxeQbehk8M-yXfDBn24Q0171%22%2C%221%2F%2F05V6Uh9jSsnYICgYIARAAGAUSNwF-L9IrV-ao76tEZMDAbf1ybmQSDJSooIQOg5Holbd1XeaNkop7Y6d6YOhBzR4n07dLnXqd3cE%22%2Cnull%5D",
            "Dnt": "1",
            "Origin": "https://www.whatbeatsrock.com",
            "Priority": "u=1, i",
            "Referer": "https://www.whatbeatsrock.com/",
            "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            }

    def __init__(self):
        self.log_file = open("guesses.txt", "w")
        self.gid = str(uuid.uuid4())
        self.prev = "rock"
        self.score = 0

        print(f"Game ID: {self.gid}")

    def save_score(self, guess):
        print(f"Saving score of {self.score}")

        data = {
                "gid": self.gid,
                "score": self.score,
                "text": f"{guess} {emoji.emojize(':globe_showing_Europe_Africa:')} did not beat {self.prev} {emoji.emojize(':globe_showing_Americas:')}",
                }

        response = requests.post(self.URL_SCORES, headers=self.HEADERS, json=data)

        print("Score saving status code: ", response.status_code)
        print("Score saving text: ", response.text)

    def log_guess(self, guess):
        self.log_file.write(f"{guess}\n")

    def make_guess(self, guess):
        self.log_guess(guess)

        print("Guess is:", guess)

        data = {
                "prev": self.prev,
                "guess": guess,
                "gid": self.gid
                }

        response = requests.post(self.URL_PLAY, headers=self.HEADERS, json=data)

        if response.status_code == 200:
            pretty_json = json.dumps(response.json(), indent=2)
            print(f"Response content: {pretty_json}")

            if response.json().get("data").get("guess_wins"):
                self.score += 1
                self.prev = guess
                return True
            else:
                self.save_score(guess)
                return False
        else:
            print(f"Error: {response.text}")
            print(f"Request status code: {response.status_code}")

            self.save_score(guess)
            return False

# Helper method
def generate_random_string(length):
    letters = string.ascii_letters  # Includes both uppercase and lowercase letters
    return ''.join(random.choice(letters) for _ in range(length))

# Usage
player = GraniteGladiator()

# Making initial guesses
player.make_guess("paper")
player.make_guess("scissors")

prv_name = "cameron"

# Infinite loop to continue making guesses until a guess fails
while True:
    cur_name = generate_random_string(30)
    guess = f"a god named {cur_name} who defeats a god named {prv_name}"
    if not player.make_guess(guess):
        break
    prv_name = cur_name

