import time
import json
import uuid
import httpx


class GraniteGladiator:
    url = "http://localhost:8080/api"
    headers = {
        "User-Agent": "Cameron's Machine",
    }

    def __init__(self):
        self.headers["Cookie"] = input("Enter your cookie: ")
        self.gid = str(uuid.uuid4())
        self.prev = "rock"
        self.score = 0
        self.client = httpx.Client()

    def save_score(self, guess):
        print(f"saving score: {self.score}")

        data = {
            "gid": self.gid,
            "score": self.score,
            "text": f"{guess} 🧑 did not beat {self.prev} 🫦",
        }

        response = self.client.post(
            f"{self.url}/scores", headers=self.headers, json=data
        )

        print(f"score saving status code: {response.status_code}")
        print(f"score saving text: {response.text}")

    def make_guess(self, guess, max_retries=3, retry_delay=5):
        print(f"guess: {guess}\tscore: {self.score}")

        data = {"prev": self.prev, "guess": guess, "gid": self.gid}

        for attempt in range(max_retries):
            try:
                response = self.client.post(
                    f"{self.url}/vs", headers=self.headers, json=data, timeout=30
                )
                print("response status code:", response.status_code)
                response.raise_for_status()

                if response.status_code == 200:
                    pretty_response_content = json.dumps(response.json(), indent=2)
                    print(f"response content: {pretty_response_content}")

                    if response.json().get("data", {}).get("guess_wins"):
                        print("Guess was correct!")
                        self.score += 1
                        self.prev = guess
                        return True
                    else:
                        self.save_score(guess)
                        return False
                else:
                    print(f"Unexpected status code: {response.status_code}")
                    return False

            except httpx.TimeoutException:
                print(f"Request timed out (attempt {attempt + 1}/{max_retries})")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    print("Rate limited, sleeping...")
                    time.sleep(600)  # Sleep for 10 minutes
                else:
                    print(f"HTTP error occurred: {e}")
                    return False
            except httpx.RequestError as e:
                print(f"An error occurred while requesting: {e}")

            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Giving up.")
                return False

        return False

    def __del__(self):
        self.client.close()


def int_to_base26(n):
    if n == 0:
        return "a"

    letters = []
    while n:
        n, r = divmod(n, 26)
        letters.append(chr(r + 97))

    return "".join(reversed(letters))


bad_guesses = set()

while True:
    player = GraniteGladiator()

    player.make_guess("paper")
    player.make_guess("scissors")

    guess = ""
    prv_name = 0
    cur_name = 0

    while True:
        cur_name = prv_name + 1
        while int_to_base26(cur_name) in bad_guesses:
            cur_name += 1

        guess = f"a God named '{int_to_base26(cur_name)}' who defeats a God named '{int_to_base26(prv_name)}'"

        if not player.make_guess(guess):
            break

        prv_name = cur_name

    print(f"losing guess: {guess}")

    bad_guesses.add(int_to_base26(cur_name))
