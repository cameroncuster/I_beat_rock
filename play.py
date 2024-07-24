import time
import json
import uuid
import requests


class GraniteGladiator:
    headers = {"User-Agent": "Cameron's Machine"}

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

        with open("scores.json", "a") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def log_guess(self, guess):
        self.log_file.write(f"{guess}\n")

    def make_guess(self, guess):
        self.log_guess(guess)
        print(f"guess: {guess}\tscore: {self.score}")

        data = {"prev": self.prev, "guess": guess, "gid": self.gid}

        response = requests.post(
            "https://www.whatbeatsrock.com/api/vs", headers=self.headers, json=data
        )

        while response.status_code == 418:
            print("rate limited, sleeping...")
            time.sleep(600)
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


bad_guesses = {}
with open("bad_guesses.txt", "r") as f:
    bad_guesses = set(f.read().split("\n"))

while True:
    player = GraniteGladiator()

    player.make_guess("paper")
    player.make_guess("scissors")

    prv_name = 0
    guess = ""
    cur_name = 0

    try:
        while True:
            cur_name = prv_name + 1
            while int_to_base26(cur_name) in bad_guesses:
                cur_name += 1
            guess = f"a God named '{int_to_base26(cur_name)}' who defeats a God named '{int_to_base26(prv_name)}'"
            if not player.make_guess(guess):
                break
            prv_name = cur_name
    except KeyboardInterrupt:
        print("interrupted...")

    print(f"losing guess: {guess}")

    player.save_score(guess)

    bad_guesses.add(int_to_base26(cur_name))
    with open("bad_guesses.txt", "w") as f:
        f.write("\n".join(bad_guesses))
