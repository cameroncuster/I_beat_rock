#!/bin/bash
curl -o fproxy.py https://raw.githubusercontent.com/cameroncuster/I_beat_rock/main/fproxy.py
curl -o requirements.txt https://raw.githubusercontent.com/cameroncuster/I_beat_rock/main/requirements.txt
sudo apt install python3-pip -y
pip install -r requirements.txt
python3 fproxy.py
