#!/bin/bash
curl -o fproxy.py https://raw.githubusercontent.com/cameroncuster/I_beat_rock/main/fproxy.py
pip install -r requirements.txt
python3 fproxy.py
