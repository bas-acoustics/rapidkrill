#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RapidKrill desktop application. It allows to perform unsupervised processing 
in all the RAW files contained in a directory.

Created on Thu Aug 15 15:34:13 2019
@author: Alejandro Ariza, British Antarctic Survey
"""

# Import modules
import os, glob, gc, logging, logging.config
import numpy as np 
from datetime import datetime as dt
from rapidkrill import read, process, report

# Log events while running
logger = logging.getLogger()
logging.config.fileConfig(os.path.join(os.path.dirname(__file__),
                                       '..','rapidkrill','logging.conf'))

def desktop(path, calfile=None, transitspeed=3,
            soundspeed=None, absorption=None):
    """
    RapidKrill desktop application. Runs unsupervised processing  in all the 
    RAW files contained in a directory. Results are stored in log/.
    
    Args:
        path         (str)       : Path to the directory containing RAW files.
        calfile      (str)       : Path to the calibration file.
        transitspeed (int, float): Minimum speed to consider the platform in 
                                   transit and proceed to process data (knots).
        soundspeed   (int, float): Sound speed to correct data (m s-1)
        absorption   (int, float): Water absorption to correct data (dB m-1)
    """
    # Get list of RAW files, and the calibration file
    rawfiles= np.sort(glob.glob(os.path.join(path, '*.raw')))    
    if rawfiles.size==0:
        raise Exception('No RAW files in directory %s' % path)
    
    # Preallocate variables and iterate through RAW files
    logname  = dt.now().strftime('D%Y%m%d-T%H%M%S')
    preraw   = None
    rawpile  = None
    for rawfile in rawfiles:
        
        # Try to read, process and report
        try:
            
            # read RAW file
            raw    = read.raw(rawfile, calfile=calfile, 
                              transitspeed=transitspeed,
                              soundspeed=soundspeed, absorption=absorption,
                              preraw=preraw)     
            preraw = raw.copy()
            
            # if raw is continuous with preceeding data...
            if raw['continuous']:
                
                # pile up current raw in the rawpile...
                if rawpile is not None:
                    rawpile = read.join(rawpile, raw)            
                
                # or start a new rawpile if not created yet
                else:
                    rawpile = raw.copy()            
            
            # or start a new rawpile if raw is not continuous         
            else:
                rawpile = raw.copy()
                prepro = None
                jdx    = [0,0]
                
            # Process rawpile if vessels is moving...
            if rawpile['transect']>0:
                
                # Process rawpile if it's got at least 1 nmi...
                if rawpile['nm'][-1]-rawpile['nm'][0]>1:
                    pro     = process.ccamlr(rawpile, prepro=prepro, jdx=jdx)
                    
                    # Report results
                    report.console(pro)
                    report.log(pro, logname)
                    
                    prepro  = rawpile                
                    jdx     = process.next_jdx(pro)
                    rawpile = None
                
                # or report it hasn't got 1 nmi yet
                else:
                    logger.info('Processing pending: at least 1 nmi required')
            
            # or report the vessel is not moving, and reset parameters        
            else:
                logger.info('Processing skipped: platform not in transit')
                rawpile = None
                prepro  = None
                jdx     = [0,0]
                
            # free up memory RAM
            if 'raw' in locals(): del raw
            if 'pro' in locals(): del pro
            gc.collect()
        
        # log error if process fails and reset rawpile        
        except Exception:
            logger.error('Failed to process file', exc_info=True)
            rawpile = None
            
# Excute desktop module if this script is run as the main program
# Fill in module's arguments from console inputs                          
if __name__ == "__main__":
    
    path=input('Enter the directory with the RAW files you want to process: ')
    if os.path.isdir(path):
        calfile=input('Enter path to calibration file (leave empty if none): ')
        if not calfile:
            desktop(path, calfile=None)
        else:                
            if os.path.exists(calfile):
                if calfile.endswith('.toml'):
                    desktop(path, calfile=calfile)
                else:
                    raise Exception(('Path to calibration file must include '+
                                     'a file with extension \'.toml\''))
            else:
                raise Exception('Calibration file %s does not exist' % calfile)               
    else:
        raise Exception('Directory %s does not exist' % path)