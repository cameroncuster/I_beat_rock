import sys
import json
import uuid
import httpx
import asyncio
import traceback
from aiohttp import web


class ProxyPool:
    def __init__(self):
        self.proxies = []

    def push_proxy(self, proxy):
        if proxy not in self.proxies:
            self.proxies.append(proxy)

    def pop_proxy(self):
        if not self.proxies:
            return None
        return self.proxies.pop(0)


proxy_pool_singleton = ProxyPool()
proxy_wait_task = None


async def wait_for_proxies():
    global proxy_wait_task
    while True:
        if proxy_pool_singleton.proxies:
            if proxy_wait_task is not None:
                proxy_wait_task.cancel()
                proxy_wait_task = None
            return
        if proxy_wait_task is None:
            proxy_wait_task = asyncio.create_task(asyncio.sleep(15))
        try:
            await proxy_wait_task
        except asyncio.CancelledError:
            pass


class Orchestrator:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def bang_proxy(self, data, path):
        host = proxy_pool_singleton.pop_proxy()

        # wait for proxies to be available
        while host is None:
            await wait_for_proxies()
            host = proxy_pool_singleton.pop_proxy()

        url = f"http://{host}:8081/{path}"

        try:
            response = await self.client.post(url, json=data)
            response.raise_for_status()
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            # TODO need more error handling
            print(f"Failed to bang proxy: {e}")
            return None

        proxy_pool_singleton.push_proxy(host)

        try:
            return response.json()
        except json.JSONDecodeError:
            print("Failed to decode response data")
            return None


class Player:
    def __init__(self):
        self.gid = str(uuid.uuid4())
        self.prev = "rock"
        self.score = 0

    async def save_score(self, orchestrator, guess):
        data = {
            "initials": "CAM",
            "gid": self.gid,
            "score": self.score,
            "text": f"{guess} 🧑 did not beat {self.prev} 🫦",
        }

        # request is sent directly from the orchestrator, no need to bang the proxies this time...
        try:
            response = await orchestrator.client.post(
                url=f"https://whatbeatsrock.com/api/scores",
                headers={
                    "Cookie": "sb-xrrlbpmfxuxumxqbccxz-auth-token=%5B%22eyJhbGciOiJIUzI1NiIsImtpZCI6IjB3Q3RxNnJ0NmpGSWs3TWEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3hycmxicG1meHV4dW14cWJjY3h6LnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIwNGE4OWUzYi02NWI4LTRkZmMtYjRiZi0yODhhYmE5N2ExNjciLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzIxOTQyNTQzLCJpYXQiOjE3MjE5Mzg5NDMsImVtYWlsIjoiY3VzdGVyLmNhbWVyb25AZ21haWwuY29tIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJnb29nbGUiLCJwcm92aWRlcnMiOlsiZ29vZ2xlIl19LCJ1c2VyX21ldGFkYXRhIjp7ImF2YXRhcl91cmwiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NMRjN6Uml6OHo1TzJkd2hRSjJUU3dOQmdaSUN5MjdJTWlldmdKdFFTZ0k1ZU5Mc1E9czk2LWMiLCJlbWFpbCI6ImN1c3Rlci5jYW1lcm9uQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmdWxsX25hbWUiOiJDYW1lcm9uIEN1c3RlciIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbSIsIm5hbWUiOiJDYW1lcm9uIEN1c3RlciIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0xGM3pSaXo4ejVPMmR3aFFKMlRTd05CZ1pJQ3kyN0lNaWV2Z0p0UVNnSTVlTkxzUT1zOTYtYyIsInByb3ZpZGVyX2lkIjoiMTE1MTU0MDI5MDk0Njc0MTg3ODM2Iiwic3ViIjoiMTE1MTU0MDI5MDk0Njc0MTg3ODM2In0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoib2F1dGgiLCJ0aW1lc3RhbXAiOjE3MjE4NDI4MDF9XSwic2Vzc2lvbl9pZCI6IjkxODlkNThhLTk0NDctNDFjNi05ODYyLTFhZjY0NzE3Njg2OCIsImlzX2Fub255bW91cyI6ZmFsc2V9.51N15MeEQ46G1H0KHnoLt2Akzwf4v9-GlY9Oa7abL48%22%2C%229L_ZGlHgj6hYoKw2uvEGhg%22%2Cnull%2Cnull%2Cnull%5D",
                    "User-Agent": "CAM",
                },
                json=data,
            )

            response.raise_for_status()
            return True
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            print(f"Failed to save score: {e}")
            return False

    async def make_guess(self, orchestrator, guess, max_retries=3):
        data = {"prev": self.prev, "guess": guess, "gid": self.gid}

        for _ in range(max_retries):
            data = await orchestrator.bang_proxy(
                data,
                "api/vs",
            )

            if data is None:
                continue

            if data["data"]["guess_wins"]:
                self.prev = guess
                self.score += 1
                return True

            await self.save_score(orchestrator, guess)
            return False

        return False


async def background_task():
    def int_to_string(n):
        if n == 0:
            return "a"

        letters = []
        while n:
            n, r = divmod(n, 26)
            letters.append(chr(r + 97))

        return "".join(reversed(letters))

    orchestrator = Orchestrator()

    bad_names = set()

    while True:
        try:
            print("Starting game...")
            player = Player()

            await player.make_guess(orchestrator, "paper")
            await player.make_guess(orchestrator, "scissors")

            prv_name = 0
            cur_name = 0

            print("Starting guessing loop...")
            while True:
                cur_name = prv_name + 1
                while int_to_string(cur_name) in bad_names:
                    cur_name += 1

                guess = f"a God named '{int_to_string(cur_name)}' who defeats a God named '{int_to_string(prv_name)}'"

                if not await player.make_guess(orchestrator, guess):
                    break

                print("Score:", player.score)

                prv_name = cur_name

            print("Final score:", player.score)

            bad_names.add(int_to_string(cur_name))
        except:
            print("Come on!")
            sys.exit(traceback.print_exc())


async def init_app():
    app = web.Application()
    app.router.add_post("/register", handle_register)

    app.on_startup.append(start_background_task)
    app.on_cleanup.append(stop_background_task)

    return app


async def handle_register(request):
    proxy_host, _ = request._transport_peername
    proxy_pool_singleton.push_proxy(proxy_host)

    return web.json_response({"status": "success"})


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
