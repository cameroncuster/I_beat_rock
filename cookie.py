import requests


def get_host():
    with open("orchestrator_host.txt", "r") as file:
        return file.readlines()[0].strip()


response = requests.post(
    f"http://{get_host()}/cookie", json={"Cookie": input("Enter cookie: ")}
)

print(response.status_code)
print(response.text)
