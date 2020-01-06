# freezer-alarm
Raspberry Pi based audio monitor to listen for freezer alarm and trigger a warning message on domestic radio if door left open.

Requires
1. Raspberry Pi-zero W or greater
2. Seeed ReSpeaker 2-Mics Pi HAT 
3. UPnP AV capable domestic radio

Two scripts are included. 
- checkFreezer.py to detect the freezer alarm has gone off.
- raiseAlarm.py to send warning message to domestic radio.

Plus supporting files
- apa102.py driver module for APA102 LEDs
- freezer.mp3 "Warning Freezer Door Open" message 

Installation
- raspian distro (or later)
- Seeed ReSpeaker 2-Mics Pi HAT drivers
- $ sudo apt-get install libasound-dev
- $ pip install pyalsaaudio

Updating to python3
The software runs on python2, standard with the raspian distro. To upgrade to python3 do
- 2to3 -w checkFreezer.py raiseAlarm.py
- $ python3 -m pip install pyalsaaudio
