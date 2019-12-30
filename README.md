# freezer-alarm
Raspberry Pi based audio monitor to listen for freezer alarm and trigger a warning message on domestic radio if door left open.

Requires
1. Raspberry Pi-zero W or greater
2. Seeed ReSpeaker 2-Mics Pi HAT 
3. UPnP AV capable domestic radio

Two scripts are included. 
- checkFreezer.py to detect the freezer alarm has gone off.
- raiseAlarm.py to send warning message to domestic radio.
