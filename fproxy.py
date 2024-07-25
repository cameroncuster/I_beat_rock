# modified from: https://github.com/JacobSteinebronn/BeatRock/blob/main/data_orchestrator.py
import json
import httpx
from aiohttp import web
import asyncio

client = httpx.AsyncClient()


# If we have a local hostfile, read it, otherwise download it
async def get_host():
    try:
        with open("master_ip.txt") as file:
            return file.readlines()[0].strip()
    except:
        fetch_response = await client.get(
            "https://raw.githubusercontent.com/cameroncuster/I_beat_rock/main/master_ip.txt"
        )
        return fetch_response._content.decode("utf-8").strip()


# Learn where the orchestrator is, and keep registering with it
async def update_orchestrator():
    print("Letting the server warm up...")
    await asyncio.sleep(5)
    while True:
        orchestrator_url = f"http://{await get_host()}/register"
        try:
            rsp = await client.post(orchestrator_url)
            if rsp.status_code == 200:
                print("Successfully (re-)registered!")
                delay = 60  # We succeeded to register, so we can probably just chill
        except httpx.ConnectError:
            print("Didn't register...")
            delay = 10  # We didn't register, so we should try again soon
        await asyncio.sleep(delay)


async def proxy_request(request):
    path = "api/" + request.match_info.get("path")

    data = await request.json()
    upstream_url = (f"https://www.whatbeatsrock.com/{path}").strip()
    headers = {
        "Cookie": request.headers.get("Cookie"),
        "User-Agent": "Sexy Beast 69",
    }

    try:
        upstream_response = await client.post(
            upstream_url, headers=headers, json=data, timeout=20
        )
    except (httpx.ConnectError, httpx.ReadTimeout):
        return web.Response(status=503)

    response_body = json.loads(upstream_response._content.decode("utf-8"))

    print(f"Proxying a {upstream_response.status_code}")
    return web.Response(
        text=json.dumps(response_body),
        status=upstream_response.status_code,
        content_type="application/json",
    )


async def init_app():
    app = web.Application()
    app.router.add_post("/api/{path}", proxy_request)

    app.on_startup.append(start_background_task)
    app.on_cleanup.append(stop_background_task)

    return app


async def start_background_task(app):
    app["background_task"] = asyncio.create_task(update_orchestrator())


async def stop_background_task(app):
    app["background_task"].cancel()
    try:
        await app["background_task"]
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    web.run_app(init_app())
