#!/bin/bash
curl -o run_orchestrator.py https://raw.githubusercontent.com/cameroncuster/I_beat_rock/main/run_orchestrator.py
curl -o requirements.txt https://raw.githubusercontent.com/cameroncuster/I_beat_rock/main/requirements.txt
sudo apt install python3-pip -y
pip install -r requirements.txt
python3 run_orchestrator.py
