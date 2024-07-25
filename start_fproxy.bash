#!/bin/bash
curl -o fproxy.py https://raw.githubusercontent.com/cameroncuster/I_beat_rock/main/fproxy.py
pip install httpx
pip install aiohttp
pip install asyncio
python3 fproxy.py
