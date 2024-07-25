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
            proxy_wait_task = asyncio.create_task(asyncio.sleep(300))
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

        url = f"http://{host}:8080/{path}"

        try:
            response = await self.client.post(url, json=data)
            response.raise_for_status()
        except Exception as e:
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
                    "User-Agent": "CAM",
                },
                json=data,
            )

            response.raise_for_status()
            return True
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

            self.prev = guess
            self.score += 1
            return True

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

    try:
        player = Player()

        await player.make_guess(orchestrator, "paper")
        await player.make_guess(orchestrator, "scissors")

        prv_name = 0
        cur_name = 0

        while True:
            cur_name = prv_name + 1
            while int_to_string(cur_name) in bad_names:
                cur_name += 1

            guess = f"a God named '{int_to_string(cur_name)}' who defeats a God named '{int_to_string(prv_name)}'"

            if not player.make_guess(orchestrator, guess):
                break

            prv_name = cur_name

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
    data = await request.json()

    proxy_host, _ = request._transport_peername
    proxy_pool_singleton.push_proxy(proxy_host)

    return web.json_response({"status": "success", "data": data})


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
