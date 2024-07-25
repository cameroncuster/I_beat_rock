import sys
import time
import json
import uuid
import httpx
import traceback
from aiohttp import web
import asyncio
from utils import int_to_base26

slave_ips = []


class Master:
    def __init__(self):
        self.slave_idx = 0
        self.client = httpx.AsyncClient()

    async def bang_proxies(self, data, path):
        slave_ip = slave_ips[self.slave_idx]
        self.slave_idx = (self.slave_idx + 1) % len(slave_ips)

        url = f"http://{slave_ip}/{path}"
        return await self.client.post(url, json=data)


class Player:
    def __init__(self):
        self.gid = str(uuid.uuid4())
        self.prev = "rock"
        self.score = 0
        self.master = Master()

    async def save_score(self, guess):
        print(f"saving score: {self.score}")

        data = {
            "initials": "CAM",
            "gid": self.gid,
            "score": self.score,
            "text": f"{guess} 🧑 did not beat {self.prev} 🫦",
        }

        response = await self.master.client.post(
            url=f"https://whatbeatsrock.com/api/scores",
            headers={
                "User-Agent": "CCC",
            },
            json=data,
        )

        print(f"score saving status code: {response.status_code}")
        print(f"score saving text: {response.text}")

    async def make_guess(self, guess, max_retries=3, retry_delay=5):
        print(f"guess: {guess}\tscore: {self.score}")

        data = {"prev": self.prev, "guess": guess, "gid": self.gid}

        for attempt in range(max_retries):
            try:
                response = await self.master.bang_proxies(
                    data,
                    "api/vs",
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
                        await self.save_score(guess)
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


proxy_wait_task = None


async def wait_for_proxies():
    global proxy_wait_task
    while True:
        if len(slave_ips):
            proxy_wait_task = None
            print("A proxy is now among us...")
            return
        if proxy_wait_task is not None:
            try:
                await proxy_wait_task
            except asyncio.CancelledError:
                pass
            proxy_wait_task = None
        else:
            proxy_wait_task = asyncio.create_task(asyncio.sleep(300))


bad_guesses = set()


async def background_task():
    try:
        print("Starting up, waiting for proxies")
        await wait_for_proxies()
        print("Got proxies!")
        player = Player()
        await player.make_guess("paper")
        await player.make_guess("scissors")
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

        bad_guesses.add(int_to_base26(cur_name))
        with open("bad_guesses.txt", "w") as f:
            f.write("\n".join(bad_guesses))

    except:
        print("Come on!")
        sys.exit(traceback.print_exc())


def push_proxy(proxy_host):
    if proxy_host in slave_ips:
        print(f"Proxy {proxy_host} already exists")
    else:
        slave_ips.append(proxy_host)
        print(f"Added proxy {proxy_host}")


async def handle_register(request):
    data = await request.json()

    proxy_host, _ = request._transport_peername
    push_proxy(proxy_host)

    return web.json_response({"status": "success", "data": data})


async def init_app():
    app = web.Application()
    app.router.add_post("/register", handle_register)

    app.on_startup.append(start_background_task)
    app.on_cleanup.append(stop_background_task)

    return app


async def start_background_task(app):
    app["background_task"] = asyncio.create_task(background_task())


async def stop_background_task(app):
    app["background_task"].cancel()
    try:
        await app["background_task"]
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    web.run_app(init_app(), port=8080)
