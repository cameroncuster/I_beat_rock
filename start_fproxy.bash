#!/bin/bash
curl -o fproxy.py https://raw.githubusercontent.com/cameroncuster/I_beat_rock/main/fproxy.py
sudo apt install python3-httpx -y
sudo apt install python3-aiohttp -y
python3 fproxy.py
