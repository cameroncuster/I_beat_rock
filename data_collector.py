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
        if proxy_wait_task is None or proxy_wait_task.done():
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

        url = f"http://{host}:8080/{path}"

        try:
            response = await self.client.post(url, json=data)
            response.raise_for_status()
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

    async def make_guess(self, orchestrator, guess, max_retries=10):
        data = {"prev": self.prev, "guess": guess, "gid": self.gid}

        for _ in range(max_retries):
            response = await orchestrator.bang_proxy(
                data,
                "api/vs",
            )

            if response is None:
                # let's give it a second to recover
                await asyncio.sleep(5)
                continue

            if response["data"]["guess_wins"]:
                self.prev = guess
                self.score += 1
                return True

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

    def string_to_int(s):
        n = 0
        for c in s:
            n = n * 26 + ord(c) - 97
        return n

    # test the helpers
    for i in range(1000):
        assert string_to_int(int_to_string(i)) == i

    orchestrator = Orchestrator()

    bad_names = set()

    while True:
        try:
            print("Starting game...")

            player = Player()

            await player.make_guess(orchestrator, "a clown")

            with open("winning_guesses.txt", "r") as f:
                lines = f.readlines()

                last_guess = lines[-1].strip()
                print("Last guess:", last_guess)

                split_guess = last_guess.split("'")
                print("Split guess:", split_guess)

                last_name_str = split_guess[1]
                print("Parsing last_name_str:", last_name_str)

                last_name = string_to_int(last_name_str)

                if not await player.make_guess(orchestrator, last_guess):
                    print("Guess failed:", last_guess)
                    raise Exception("Failed to enter the guessing loop")

            print("Starting guessing loop...")
            while True:
                name = last_name + 1
                while name in bad_names:
                    name += 1

                guess = f"a God named '{int_to_string(name)}' who defeats a God named '{int_to_string(last_name)}'"

                if not await player.make_guess(orchestrator, guess):
                    bad_names.add(name)
                    break

                with open("winning_guesses.txt", "a") as f:
                    f.write(f"{guess}\n")

                last_name = name

                print("Guess:", guess)
                print("Currently have:", len(proxy_pool_singleton.proxies), "proxies")

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
