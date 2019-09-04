#!/bin/bash
# This is the startup script for RAPIDKRILL that is called by systemd.
# Change the mount line below to use your specific network share and
# credentials.
umount /home/pi/data
mount -t cifs -o uid=$(id -u),gid=$(id -g),username=username,password=password //helium/shared /home/pi/data
export PYTHONPATH=/home/pi/.local/lib/python3.6/site-packages:/home/pi/src/PyEcholab2:/home/pi/src/rapidkrill
cd /home/pi/src/rapidkrill/routines/rapidkrill
/home/pi/berryconda3/bin/python rk.py /home/pi/data
