# hamtools
Ham Related Tools

## cwdtrd
cwdtrd is a daemon which runs in the background, and accepts characters to send to Yaesu radios that have both STANDARD and ENHANCED serial ports.
cwdtrd use the STANDARD port which is the one higher than the CAT/PTT port. It defaults to /dev/ttyUSB1

cwdtrd is written in python 3, and needs to have pyserial installed via pip.

NOTE: I wrote this in a UV environment, so if you do not use the uv venv then simply add this to the top line of the file:

**#!/usr/bin/env python**

### Prerequisites

**NOTE** for this to work, you must be in the **dialout** group

1. do $ **id**
2. if it doesn't show dialout, you must add yourself to the dialout group, and REBOOT.
3. to add yourself in the dialout group do $ **sudo usermod -aG dialout <your_user_name>**
4. sudo reboot (or reboot by any other means).


Read the comments in the file for how to set up your radio:

For the FTX-1 it was simple:
1. in CW Settings, set keying to DTR
2. set BK-IN to on
3. set your radio's mode to either CW-U or CW-L

Similar for other Yaesu radio's.

### Usage

make sure to do a $ **chmod +x cwdtrd**, and put it in your path

$ **cwdtrd -h** will give you help, and to see the parameters and their defaults.

To Run with default values:

$ **cwdtrd**

To send characters:

$ **echo "cq cq de wf5w" | nc localhost 9999**

$ **echo "w5pyr ur 599 599 MS" | nc 127.0.0.1 9999**

you can run this daemon on another host in your local network, if you run it as the default 0.0.0.0

so, lets say you run the daemon on host 192.168.1.205 where your radio is hooked to, and from your local machine ( 192.168.1.217 )

$ **echo "cq cq de wf5w" | nc 192.168.1.205 9999**

## sendcw

This is a helper script to do the above echo to netcat. It is probably easier in the heat of the moment, while doing a QSO.

### usage

make sure to do a $ **chmod +x sendcw**, and put it in your path

each of these is valid, depending upon how and where on the network, you started up the cwdtrd daemon

**sendcw** -- prints the usage statement and exits

**sendcw** cq de wf5w

**sendcw -h 192.168.1.218 cq de wf5w**

**sendcw -h 192.168.1.218 -p 8888 cq de wf5w**
