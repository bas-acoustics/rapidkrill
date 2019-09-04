#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script to run shipdemo.py

shipdemo copies RAW files to a "collector" folder, simulating an echosounder
when collecting data. shipdemo is useful for testing the RapidKrill listening
routine.

Created on Thu Aug 15 12:40:32 2019
@author: Alejandro Ariza, British Antarctic Survey
"""

#------------------------------------------------------------------------------
# import shipdemo
from shipdemo import shipdemo

#------------------------------------------------------------------------------
# Set the time rate (seconds) at which you want to move the RAW files
tr = 10

# 10 seconds is fine to quickly check how the RapidKrill listening routine 
# handles the incoming files. However, this is unusual for echosounders. For 
# example, an EK60 echosounder collecting multifrequency data down to 1000 m 
# depth at a 2-seconds ping rate can take 5 minutes to generate a 25 Mb RAW 
# file. RapidKrill takes about 1-2 minutes to read, process, and report results
# for the same size RAW file, depending of your computer. So, if you run 
# shipdemo with time rates below 1-2 minutes, you will see how the incoming RAW
# files are piled up in a "pending processing list". 

#------------------------------------------------------------------------------
# Run shipdemo
shipdemo(timerate=tr)