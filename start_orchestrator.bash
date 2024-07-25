#!/bin/bash
curl -o run_orchestrator.py https://raw.githubusercontent.com/cameroncuster/I_beat_rock/main/run_orchestrator.py
sudo apt install python3-httpx -y
sudo apt install python3-aiohttp -y
python3 run_orchestrator.py
