import requests

cookie = input("Enter the cookie: ")
gid = input("Enter the game id: ")
score = input("Enter the score: ")
guess = input("Enter the final guess: ")
prev = input("Enter the previous guess: ")

headers = {"Cookie": cookie, "User-Agent": "Cameron's Machine"}

data = {
    "gid": gid,
    "score": score,
    "text": f"{guess} 🧑 did not beat {prev} 🫦",
}

response = requests.post("https://www.whatbeatsrock.com/api/scores", headers, json=data)

print(f"score saving status code: {response.status_code}")
print(f"score saving text: {response.text}")
