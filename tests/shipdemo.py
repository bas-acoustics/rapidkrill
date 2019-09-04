#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ship's echosounder emulator.

Created on Mon Aug 12 09:53:31 2019
@author: Alejandro Ariza, British Antarctic Survey
"""

# get modules
import os, glob, time, logging, logging.config
import numpy as np
from shutil import copyfile

# log events while running
logger = logging.getLogger()
logging.config.fileConfig(os.path.join(os.path.dirname(__file__),
                                       '..','rapidkrill','logging.conf'))
def shipdemo(timerate=300):
    """
    Emulates an echosounder storing RAW files in a directory, imitating the
    ship's setup. Files are sequentially copied from folder "echosounder" to 
    folder "collector" at a user-defined time rate. Any RAW file previously 
    present in the collector will be removed before start the copying process.
    
    Args:
        timerate (int): time rate at which the files will be stored (seconds)    
    """
    
    # get collector and echosounder directories
    collector   = os.path.join(os.path.dirname(__file__), 'collector'  ,'')
    echosounder = os.path.join(os.path.dirname(__file__), 'echosounder','')
    
    # get the list of RAW files in collector and echosounder
    craws = np.sort(glob.glob(collector   + '*.raw'))
    eraws = np.sort(glob.glob(echosounder + '*.raw'))
    if eraws.size is 0:
        raise Exception('No RAW files in the echosounder directory')
        
    # remove RAW files previously stored in the collector
    for craw in craws:
        os.remove(craw)
    
    # copy RAW files from the echosounder to the collector    
    for i, eraw in enumerate(eraws):
        if i is not 0:
            for tr in range(timerate, 0, -1):
                print('\rNext file in %s seconds...' % str(tr).zfill(2),end='') 
                time.sleep(1)
        print('\r', end='')
        logger.info('Copying file %s of %s: %s...'
              %(str(i+1).zfill(2), len(eraws), os.path.split(eraw)[-1]))    
        copyfile(eraw, collector + os.path.split(eraw)[-1])
        
    print('shipdemo finished')  

# excute shipdemo if this script is run as the main program     
if __name__ == '__main__':
    shipdemo()