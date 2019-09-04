#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example to use the Rapidkrill desktop application. This will allow you to 
perform unsupervised processing in all the RAW files contained in a directory.
 
Created on Thu Aug 15 13:10:02 2019
@author: Alejandro Ariza, British Antarctic Survey
"""

#------------------------------------------------------------------------------
# set the rapidkrill library as the working directory
import os 
wd = os.path.join(os.path.dirname(__file__), '..','rapidkrill','')
os.chdir(wd)

#------------------------------------------------------------------------------
# Get path to the directory "echosounder"
path = os.path.join(os.path.dirname(__file__),'echosounder','')

#------------------------------------------------------------------------------
# import RapidKrill desktop module, and process all RAW files in the directory
from rapidkrill.desktop import desktop
desktop(path)

# Check results in the console and in the "log" folder.