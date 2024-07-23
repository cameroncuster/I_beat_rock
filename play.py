import json
import uuid
import emoji
import string
import random
import requests

class GraniteGladiator:
    # Class Constants
    URL = "https://www.whatbeatsrock.com/api/vs"
    HEADERS = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
            }

    LOG_FILE_NAME = "guesses.txt"

    def __init__(self):
        self.log_file = open(self.LOG_FILE_NAME, "w")
        self.gid = str(uuid.uuid4())
        self.prev = "rock"
        self.score = 0
        print(f"Game ID: {self.gid}")

    def save_score(self, guess):
        data = {
                "initials": "camc",
                "score": self.score,
                "gid": self.gid,
                "text": f"{guess} {emoji.emojize(':globe_showing_Europe_Africa:')} did not beat {self.prev} {emoji.emojize(':globe_showing_Americas:')}",
                }

        response = requests.post("https://www.whatbeatsrock.com/api/score", headers=self.HEADERS, json=data)
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

        response = requests.post(self.URL, headers=self.HEADERS, json=data)

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

