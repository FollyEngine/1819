#!/bin/bash
git pull
python ./src/RPi/$HOSTNAME/main.py >> local.log
