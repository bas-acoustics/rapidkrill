## RapidKrill Tutorial

This document describes how to run RapidKrill. It is assumed that you already have installed the library, see [installation instructions](installation.md) if not.

RapidKrill can run on Mac OS, Linux and Windows. If you are running RapidKrill on a Raspberry Pi, see this [additional information](raspberry_pi.md). 

### Run Listening routine
This mode is used for live echosounder data, e.g, on-board the ship, as follows:

Change to the `rapidkrill` directory, e.g: 
```
cd ~/src/rapidkrill
```

Run ipython in the terminal.
```
ipython
```

Import the RapidKrill listening module
```
from rapidkrill.listen import listen
```

Listen for new RAW files in the echosounder directory (this might be a local directory on the echosounder PC or a directory mounted over the network, see [raspberry_pi.md](raspberry_pi.md) for futher information).

Provide the name of your platform, and the email address to send out reports.
```
listen(‘/path/to/echosounder/directory’, platform=‘MyShip’, recipient=‘landstation@email.com’)
```

You also can apply new calibration parameters, speed of sound, and absorption to correct the data that will be processed. E.g:
```
listen(‘/path/to/mounted/collector’, platform=‘MyShip’, recipient=‘landstation@email.com’,
       calfile=‘path/to/calfile.toml’, soundspeed=1500, absorption=0.01)
```

### Run Desktop routine
This mode is used offline, e.g, for processing historic datasets, as follows:

Change to the `rapidkrill` directory, e.g: 
```
cd ~/src/rapidkrill
```

Run ipython in the terminal.
```
ipython
```

Import RapidKrill desktop module.
```
from rapidkrill.desktop import desktop
```

Run RapidKrill processing routine over all the RAW files in a directory.
```
desktop(‘path/to/rawfile/directory’)
```
Without further calibration information, the Rapidkrill processing routine uses the echosounder calibration parameters (TS gain and Sa correction) and sound speed and absoprtion coefficients within the raw file.

You also can apply new calibration parameters, speed of sound, and absorption to correct the data that will be processed using a [calibration file](https://github.com/bas-acoustics/krill-ball/blob/master/ZDLP-D20091210-cal.toml). E.g:
```
desktop(‘path/to/rawfile/directory’,
        calfile=‘path/to/calfile.toml’, soundspeed=1500, absorption=0.027)
```
