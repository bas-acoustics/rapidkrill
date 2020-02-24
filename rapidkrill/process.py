#!/usr/bin/env python3
"""
RapidKrill processing routine.

Created on Wed Apr 10 15:41:48 2019
@author: Alejandro Ariza, British Antarctic Survey
"""

# import modules
import os
import numpy as np
import logging, logging.config
from scipy.signal import convolve2d
from scipy.interpolate import interp1d
from echopy import transform as tf
from echopy import resample as rs
from echopy import mask_impulse as mIN
from echopy import mask_seabed as mSB
from echopy import get_background as gBN
from echopy import mask_signal2noise as mSN
from echopy import mask_range as mRG
from echopy import mask_shoals as mSH

# log events while running
logger = logging.getLogger()
logging.config.fileConfig(os.path.join(os.path.dirname(__file__),'logging.conf'))

def ccamlr(raw, prepro=None, jdx=[0,0]):
    """
    CCAMLR processing routine.
    
    Process EK60 raw data and returns its variables in a dictionary array.
    """
    #--------------------------------------------------------------------------
    # check for appropiate inputs
    if (isinstance(prepro, dict)) & (jdx[0]>=0):
        raise Exception('Preceeding raw data needs appropiate j indexes')
        
    #--------------------------------------------------------------------------       
    # Load variables
    rawfiles    = raw['rawfiles']
    transect    = raw['transect']
    alpha120    = raw['alpha'   ]
    r120        = raw['r'       ]    
    t120        = raw['t'       ]
    lon120      = raw['lon'     ]
    lat120      = raw['lat'     ]
    nm120       = raw['nm'      ]
    km120       = raw['km'      ]
    knt120      = raw['knt'     ]     
    kph120      = raw['kph'     ]
    pitchmax120 = raw['pitchmax']
    rollmax120  = raw['rollmax' ]
    heavemax120 = raw['heavemax']
    Sv120       = raw['Sv'      ]
    theta120    = raw['theta'   ]
    phi120      = raw['phi'     ]
    
    #--------------------------------------------------------------------------    
    # join preceeding raw data, if there is continuity in the transect
    if prepro is not None:
        if prepro['transect']==raw['transect']:
            t120     = np.r_[prepro['t'    ][   jdx[0]:], t120    ]
            lon120   = np.r_[prepro['lon'  ][   jdx[0]:], lon120  ]
            lat120   = np.r_[prepro['lat'  ][   jdx[0]:], lat120  ]
            nm120    = np.r_[prepro['nm'   ][   jdx[0]:], nm120   ]
            km120    = np.r_[prepro['km'   ][   jdx[0]:], km120   ]
            knt120   = np.r_[prepro['knt'  ][   jdx[0]:], knt120  ]
            kph120   = np.r_[prepro['kph'  ][   jdx[0]:], kph120  ]
            Sv120    = np.c_[prepro['Sv'   ][:, jdx[0]:], Sv120   ]
            theta120 = np.c_[prepro['theta'][:, jdx[0]:], theta120]
            phi120   = np.c_[prepro['phi'  ][:, jdx[0]:], phi120  ]
        else:
            jdx[1]=0
    else:
        jdx[1]=0 
    
    #--------------------------------------------------------------------------    
    # report about the transects being processed
    trsct = np.arange(jdx[1], nm120[-1],   1)
    logger.info('Processing transect %03d : %2.2f - %2.2f nmi...'
                % (transect, trsct[0], trsct[-1]))

    #--------------------------------------------------------------------------       
    # Clean impulse noise      
    Sv120in, m120in_ = mIN.wang(Sv120, thr=(-70,-40), erode=[(3,3)],
                                dilate=[(7,7)], median=[(7,7)])
    #TODO: True is valid
    # -------------------------------------------------------------------------
    # estimate and correct background noise       
    p120           = np.arange(len(t120))                
    s120           = np.arange(len(r120))                
    bn120, m120bn_ = gBN.derobertis(Sv120, s120, p120, 5, 20, r120, alpha120)
    Sv120clean     = tf.log(tf.lin(Sv120in) - tf.lin(bn120))
    #TODO: True is valid
    # -------------------------------------------------------------------------
    # mask low signal-to-noise 
    m120sn             = mSN.derobertis(Sv120clean, bn120, thr=12)
    Sv120clean[m120sn] = -999
    
    # -------------------------------------------------------------------------
    # get mask for near-surface and deep data
    m120rg = mRG.outside(Sv120clean, r120, 19.9, 250)
    
    # -------------------------------------------------------------------------
    # get mask for seabed
    m120sb = mSB.ariza(Sv120, r120, r0=20, r1=1000, roff=0,
                       thr=-38, ec=1, ek=(3,3), dc=10, dk=(3,7))
    
    # -------------------------------------------------------------------------
    # get seabed line
    idx                = np.argmax(m120sb, axis=0)
    sbline             = r120[idx]
    sbline[idx==0]     = np.inf
    sbline             = sbline.reshape(1,-1)
    sbline[sbline>250] = np.nan
    
    # -------------------------------------------------------------------------
    # get mask for non-usable range    
    m120nu = mSN.fielding(bn120, -80)[0]
    
    # -------------------------------------------------------------------------
    # remove unwanted (near-surface & deep data, seabed & non-usable range)
    m120uw = m120rg|m120sb|m120nu
    Sv120clean[m120uw] = np.nan
    
    # -------------------------------------------------------------------------
    # get swarms mask
    k = np.ones((3, 3))/3**2
    Sv120cvv = tf.log(convolve2d(tf.lin(Sv120clean), k,'same',boundary='symm'))   
    m120sh, m120sh_ = mSH.echoview(Sv120cvv, r120, km120*1000, thr=-70,
                                   mincan=(3,10), maxlink=(3,15), minsho=(3,15))
     
    # -------------------------------------------------------------------------
    # get Sv with only swarms
    Sv120sw                    = Sv120clean.copy()
    Sv120sw[~m120sh & ~m120uw] = -999
    
    # -------------------------------------------------------------------------
    # resample Sv from 20 to 250 m, and every 1nm     
    r120intervals                     = np.array([20, 250])
    nm120intervals                    = np.arange(jdx[1], nm120[-1],   1) 
    Sv120swr, r120r, nm120r, pc120swr = rs.twod(Sv120sw, r120, nm120,
                                                r120intervals, nm120intervals,
                                                log=True)
        
    # -------------------------------------------------------------------------
    # remove seabed from pc120swr calculation, only water column is considered
    m120sb_             = m120sb*1.0
    m120sb_[m120sb_==1] = np.nan
    pc120water          = rs.twod(m120sb_, r120, nm120,
                                  r120intervals, nm120intervals)[3]
    pc120swr            = pc120swr/pc120water * 100
    
    # -------------------------------------------------------------------------
    # resample seabed line every 1nm
    sbliner = rs.oned(sbline, nm120, nm120intervals, 1)[0]
    
    # -------------------------------------------------------------------------
    # get time resampled, interpolated from distance resampled
    epoch  = np.datetime64('1970-01-01T00:00:00')
    t120f  = np.float64(t120 - epoch)    
    f      = interp1d(nm120, t120f)
    t120rf = f(nm120r)
    t120r  = np.array(t120rf, dtype='timedelta64[ms]') + epoch
    
    t120intervalsf = f(nm120intervals)
    t120intervals  = np.array(t120intervalsf, dtype='timedelta64[ms]') + epoch
    
    # -------------------------------------------------------------------------
    # get latitude & longitude resampled, interpolated from time resampled
    f       = interp1d(t120f, lon120)
    lon120r = f(t120rf)
    f       = interp1d(t120f, lat120)
    lat120r = f(t120rf)
    
    # -------------------------------------------------------------------------
    # resample back to full resolution  
    Sv120swrf, m120swrf_   = rs.full(Sv120swr, r120intervals, nm120intervals, 
                                     r120, nm120)
    #TODO: True is valid
    
    # -------------------------------------------------------------------------
    # compute Sa and NASC from 20 to 250 m or down to the seabed depth
    Sa120swr   = np.zeros_like(Sv120swr)*np.nan
    NASC120swr = np.zeros_like(Sv120swr)*np.nan
    for i in range(len(Sv120swr[0])):
        if (np.isnan(sbliner[0,i])) | (sbliner[0,i]>250):
            Sa120swr  [0,i] = tf.log(tf.lin(Sv120swr[0,i])*(250-20))
            NASC120swr[0,i] = 4*np.pi*1852**2*tf.lin(Sv120swr[0,i])*(250-20)
        else:
            Sa120swr  [0,i] = tf.log(tf.lin(Sv120swr[0,i])*(sbliner[0,i]-20))
            NASC120swr[0,i] = 4*np.pi*1852**2*tf.lin(Sv120swr[0,i])*(sbliner[0,i]-20)
    
    # -------------------------------------------------------------------------
    # return processed data outputs
    m120_ = m120in_ | m120bn_ | m120sh_ | m120swrf_
    #TODO: True is valid

    pro = {'rawfiles'       : rawfiles   , # list of rawfiles processed
           'transect'       : transect   , # transect number
           'r120'           : r120       , # range (m)
           't120'           : t120       , # time  (numpy.datetime64)
           'lon120'         : lon120     , # longitude (deg)
           'lat120'         : lat120     , # latitude (deg)
           'nm120'          : nm120      , # distance (nmi)
           'km120'          : km120      , # distance (km)
           'knt120'         : knt120     , # speed (knots)
           'kph120'         : kph120     , # speed (km h-1)
           'pitchmax120'    : pitchmax120, # max value in last pitching cycle (deg)
           'rollmax120'     : rollmax120 , # max value in last rolling cycle (deg)
           'heavemax120'    : heavemax120, # max value in last heave cycle (deg)
           'Sv120'          : Sv120      , # Sv (dB)
           'theta120'       : theta120   , # Athwart-ship angle (deg)
           'phi120'         : phi120     , # Alon-ship angle (deg)
           'bn120'          : bn120      , # Background noise (dB)
           'Sv120in'        : Sv120in    , # Sv without impulse noise (dB)
           'Sv120clean'     : Sv120clean , # Sv without background noise (dB)          
           'Sv120sw'        : Sv120sw    , # Sv with only swarms (dB)
           'nm120r'         : nm120r     , # Distance resampled (nmi)
           'r120intervals'  : r120intervals, # r resampling intervals
           'nm120intervals' : nm120intervals, # nmi resampling intervals
           't120intervals'  : t120intervals, # t resampling intervals
           'sbliner'        : sbliner    , # Seabed resampled (m)
           't120r'          : t120r      , # Time resampled (numpy.datetime64)
           'lon120r'        : lon120r    , # Longitude resampled (deg)
           'lat120r'        : lat120r    , # Latitude resampled (deg)
           'Sv120swr'       : Sv120swr   , # Sv with only swarms resampled (dB)
           'pc120swr'       : pc120swr   , # Valid samples used to compute Sv120swr (%)
           'Sa120swr'       : Sa120swr   , # Sa from swarms, resampled (m2 m-2)
           'NASC120swr'     : NASC120swr , # NASC from swarms, resampled (m2 nmi-2)
           'Sv120swrf'      : Sv120swrf  , # Sv with only swarms, resampled, full resolution (dB)         
           'm120_'          : m120_      } # Sv mask indicating valid processed data (where all filters could be applied)
    
    return pro

def next_jdx(pro):
    """
    Compute j indexes indicating which pings from the current file are not
    processed due to edge issues. These pings will be concatenated before the 
    next file in the sequence so that they will be processed together.
    
    Args:
        pro (dict): Processed data output from ccamlr function.
        
    Returns:
        tuple : 2-elements j index.
        
    Notes:
        Often, resampling and many other processing algorithms cannot be
        performed nearby the array borders, leaving not-processed samples in
        the processed array (NANs). That can be easily seen in the along-time 
        dimension as empty pings at the beginning and at the end of processed 
        arrays (see figure and legend below). To prevent this to happen, when 
        processing several files in a sequence, the last pings not processed in
        the current file are placed right before (and processed together with) 
        pings of next file. This routine is performed in the ccamlr processing
        routine above. This function computes a j index to work out which pings
        from the current file need to go together with the next file. As a 
        consequence, there is a missmatch between raw and processed timestamps
        when processing in sequence mode. See figure and legend below.
            
    Figure:    
        · · · · · · · · · · · · · · · · · · · · · · ·  
        ·|x x x x x x x|x x x x x x x|x x x x x x x|· (raw) 
        ·|o o x x x o o|o o x x x o o|o o x x x o o|· (processed)
        · · ·|x x x|x x x x x x x|x x x x x x x|· · · (processed in sequence)
        · · · · · · · · · · · · · · · · · · · · · · ·  
    
    Legend:
        x -> ping
        o -> empty ping after processing
        | -> file separator
        · -> timestamp grid    
    """    
    
    # jbool = np.sum(pro['m120_'], axis=0)>1 
    jbool = pro['m120_'].all(axis=0)          
    jdx0  = np.where(~jbool)[0][-1] - np.where(~jbool)[0][0] - len(jbool) + 1
    jdx1  = pro['nm120intervals'][-1]
    jdx   = [jdx0, jdx1] 
    
    return jdx 