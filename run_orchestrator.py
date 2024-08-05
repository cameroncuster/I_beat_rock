import sys
import json
import uuid
import httpx
import asyncio
import traceback
from aiohttp import web

target = 100


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


cookie = "Nom nom"


class Player:
    def __init__(self):
        self.gid = str(uuid.uuid4())
        self.prev = "rock"
        self.score = 0

    async def save_score(self, orchestrator, guess):
        data = {
            "gid": self.gid,
            "score": self.score,
            "text": f"{guess} 🤖 did not beat {self.prev} 🤠",
        }

        # request is sent directly from the orchestrator, no need to bang the proxies this time...
        try:
            response = await orchestrator.client.post(
                url="https://www.whatbeatsrock.com/api/scores",
                headers={
                    "Cookie": cookie,
                    "User-Agent": "CAM",
                },
                json=data,
            )

            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to save score: {e}")
            return False

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

    async def lose(self, orchestrator):
        if not await self.make_guess(
            orchestrator, "Thanos with a full infinity gauntlet"
        ):
            print("Failed to lose")
            return
        if await self.make_guess(orchestrator, "camc FTW ;)"):
            print("We won with: camc FTW ;)")
            if await self.make_guess(orchestrator, "a useless rock"):
                # this should never happen
                print("We won with: a useless rock -- this state should be unreachable")
            await self.save_score(orchestrator, "a useless rock")
            return
        print("Saving score...")
        await self.save_score(orchestrator, "camc FTW ;)")


async def background_task():
    orchestrator = Orchestrator()
    player = Player()

    try:
        print("Starting game with id:", player.gid)
        with open("winning_guesses.txt", "r") as f:
            lines = f.readlines()

            # let's just ensure a strict majority
            assert len(lines) > target

            for i in range(target):
                guess = lines[i]

                print("Score:", player.score, "with target of", target)
                print("Currently have:", len(proxy_pool_singleton.proxies), "proxies")

                if not await player.make_guess(orchestrator, guess.strip()):
                    raise Exception("Guess failed")

            await player.lose(orchestrator)

            print("Final score:", player.score)

            sys.exit(0)

    except:
        print("Come on!")
        sys.exit(traceback.print_exc())


async def init_app():
    app = web.Application()
    app.router.add_post("/register", handle_register)
    app.router.add_post("/cookie", handle_cookie)

    app.on_startup.append(start_background_task)
    app.on_cleanup.append(stop_background_task)

    return app


async def handle_register(request):
    proxy_host, _ = request._transport_peername
    proxy_pool_singleton.push_proxy(proxy_host)
    return web.json_response({"status": "success"})


async def handle_cookie(request):
    global cookie
    data = await request.json()
    try:
        cookie = data["Cookie"]
        print(f"Cookie updated: {cookie}", flush=True)
        return web.json_response({"status": "success"})
    except Exception as e:
        print(f"Failed to update cookie: {e}")
        return web.json_response({"status": "failed"})


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
