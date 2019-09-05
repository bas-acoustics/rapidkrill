#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RapidKrill listening routine. Runs unsupervised processing over RAW files that
are being stored by an EK60 echosounder in real-time. 

Created on Mon Aug 12 15:27:10 2019
@author: Alejandro Ariza, British Antarctic Survey
"""

# import modules
import re, os, time, gc, logging, logging.config, datetime
from rapidkrill import read, process, report

# log events while running
logger = logging.getLogger()
logging.config.fileConfig(os.path.join(os.path.dirname(__file__),'logging.conf'))

def listen(path, calfile=None, platform='Unknown',
           savepng=False, reportrows=10, recipient=None):
    
    """
    Listen for new raw files. When find a new one, it carries out the following
    actions:
        1) Read RAW data
        2) Process RAW data (calibration, de-noising and target identification)
        3) Report (summarise and deliver results)
    
    Results are stored in log/.
    
    Args:
        path    (str): Path to the directory where the RAW files are copied
                       by the echosounder.
        calfile (str): Path to the calibration file.        
    """
    
    # Check if recipient email has been provided
    if recipient is None:
        raise Exception('Need to provide a recipient email address')
    
    # Report path being listened
    logger.info('Listening at %s...', path)
     
    # List preceeding RAW files in the directory
    r = re.compile('.*raw$')
    pre = [f for f in os.listdir(path) if r.match(f, re.IGNORECASE)]
    pre.sort()
       
    # Preallocate variables and loop forever
    logname = datetime.datetime.now().strftime('D%Y%m%d-T%H%M%S')
    preraw  = None
    rawpile = None
    alr     = []
    t       = '\n\t\t\t\t\t      > '
    lastrow = 0
    while 1:        
        
        # List cumulated RAW files in the directory (preceeding + newcomers)
        time.sleep(10)     
        cum = [f for f in os.listdir(path) if r.match(f, re.IGNORECASE)]
        cum.sort()
        
        # Report of "No new files", if cumulated and preeceding are equal
        if len(cum)==len(pre):
            logger.info('No new files')
        
        # Reset list of preeceding files, if files have been deleted
        if len(cum)<len(pre):
            logger.warning('Files have been deleted!')
            pre = cum.copy()
        
        # Identify new files as the difference between cumulated and preceeding
        if len(cum)>len(pre):
            new = cum.copy()
            for filename in pre:
                new.remove(filename)   
            
            # Identify repeated files (already processed but incoming again)
            rep = list(set(new) & set(alr))
            if len(rep)>0:
                rep.sort()
                rep.insert(0, 'Inconming files already processed:')
                logger.warning(t.join(rep))
                rep.remove('Inconming files already processed:')
                for filename in rep:                   
                    new.remove(filename)
                    pre.append(filename)
                pre=list(set(pre))
            
            # Report list of new files pending to be processed
            if len(new)>0:
                new.insert(0, 'Files pending:')
                if len(new)>3:
                    logger.info(t.join(new[:3]+['+ '+str(len(new)-3)+' more']))
                else:
                    logger.info(t.join(new))
                new.remove('Files pending:')                
            
            # If more than one new file, try to process the first one
            if (len(new))>1:       
                try:
                    
                    # Move file name to preceeding & already-processed lists
                    pre.append(new[0])
                    alr.append(new[0])
                    
                    # Read RAW
                    rawfile = os.path.join(path, new[0])
                    raw     = read.raw(rawfile, calfile=calfile, preraw=preraw)     
                    preraw  = raw.copy()
                    
                    # If raw data is continuous with preceeding data...
                    if raw['continuous']:
                        
                        # pile up current raw data in the rawpile
                        if rawpile is not None:
                            rawpile = read.join(rawpile, raw)            
                        
                        # or start a new rawpile if not created yet
                        else:
                            rawpile = raw.copy()            
                    
                    # Start a new rawpile if raw is not continuous         
                    else:
                        rawpile = raw.copy()
                        prepro = None
                        jdx    = [0,0]
                        
                    # Process rawpile if vessels is moving...
                    if rawpile['transect']>0:
                        
                        # Process rawpile if it's got at least 1 nmi...
                        if rawpile['nm'][-1]-rawpile['nm'][0]>1:
                            pro = process.ccamlr(rawpile,prepro=prepro,jdx=jdx)
                            
                            # Report results
                            report.console(pro)
                            report.log(pro, logname, savepng=savepng)
                            try:
                                lastrow = report.land(logname, lastrow,
                                                      reportrows,
                                                      platform=platform, 
                                                      recipient=recipient)
                            except Exception:                                       
                                logger.error('Failed to send report',exc_info=True)
                            prepro  = rawpile                
                            jdx     = process.next_jdx(pro)
                            rawpile = None
                        
                        # or report it hasn't got 1 nmi yet
                        else:
                            logger.info('Processing pending: at least ' +
                                        '1 nmi required')
                    
                    # or report the vessel is not moving, and reset parameters
                    else:
                        logger.info('Processing skipped: ' + 
                                    'platform not in transit')
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

# Excute listen module if this script is run as the main program
# Fill in module's arguments from console inputs                        
if __name__ == "__main__":
    
    path=input('Enter the directory you want to listen to: ')
    if os.path.isdir(path):
        calfile=input('Enter path to calibration file (leave empty if none): ')
        if not calfile:
            listen(path, calfile=None)
        else:                
            if os.path.exists(calfile):
                listen(path, calfile=calfile)           
            else:
                raise Exception('Calibration file %s does not exist' % calfile)               
    else:
        raise Exception('Directory %s does not exist' % path)