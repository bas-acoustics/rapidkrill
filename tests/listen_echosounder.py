#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script to test the RapidKrill listening routine.

Created on Thu Aug 15 12:35:04 2019
@author: Alejandro Ariza, British Antarctic Survey
"""

#------------------------------------------------------------------------------
# set the rapidkrill library as the working directory
import os 
wd = os.path.join(os.path.dirname(__file__), '..','rapidkrill','')
os.chdir(wd)

#------------------------------------------------------------------------------
# import listen module, and listen for new RAW files in the collector directory
from rapidkrill.listen import listen
collector = os.path.join(os.path.dirname(__file__),'collector','')
listen(collector)

# Getting "No new files" all the time? Well, you need to turn on your 
# echosounder and collect some new RAW files!

# Don't panic if you don't have an echosounder handy. Just put some RAW files
# in the "echosounder" directory and run shipdemo.py in a new console. This 
# program will sequentially copy the RAW files from "echosounder" to 
# "collector" folders at a user-defined time rate, simulating the echosounder 
# operation at sea. This way you'll be able to test the RapidKrill listen 
# routine without having an echosounder collecting data at this moment.

# There is a script ready for this in the test directory: run_shipdemo.py