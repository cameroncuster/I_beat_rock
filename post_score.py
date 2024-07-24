import json
import requests

cookie = input("Enter your cookie: ")

headers = {"Cookie": cookie, "User-Agent": "Cameron's Machine"}

with open("scores.json", "r") as file:
    for line in file:
        score = json.loads(line)

        data = {
            "gid": score["gid"],
            "score": score["score"],
            "text": score["text"],
        }

        response = requests.post(
            "https://www.whatbeatsrock.com/api/scores", headers, json=data
        )

        print(f"score saving status code: {response.status_code}")
        print(f"score saving text: {response.text}")
