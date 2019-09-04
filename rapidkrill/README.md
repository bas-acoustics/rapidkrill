# RAPIDKRILL

## Introduction

This directory mainly contains RASPBERRY PI specific RAPIDKRILL code.

## Notes

Unfortunately, inotify does not work for file systems mounted via CIFS
(i.e. Windows Shares) and so we have to poll the filesystem for
changes rather than receive change notifications.

We tried using the Fedora/ARM Linux distribution, it worked but seemed
very slow.

RAPIDKRILL uses recent versions of `numpy` and `matplotlib`. Packages
on Raspberry Pi can be slightly older and, at the time of writing,
there are some issues with using `numpy.datetime64` in calls to
`matplotlib`. This only affects the plotting of echograms.

If accessing the pi remotely, it can be useful to use the `-X` flag to
ssh to enable X forwarding and thus see generated graphics. Warning -
it can be very slow.

You can follow the log file using:

```
journalctl -fu rapidkrill.service
```
