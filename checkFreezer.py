#!/usr/bin/env python
#https://www.raspberrypi.org/forums/viewtopic.php?t=35838&p=454041
# 8 bar Audio equaliser using MCP2307

"""
MIT License

Copyright (c) 2020 William Pringle

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import alsaaudio as aa
import smbus
from struct import unpack
import numpy as np
import subprocess,time
import atexit

import apa102  # for LED strip

def find_maximum(data,target=0,triggerdelta=0):
    # Convert raw data to numpy array
    data = unpack("%dh"%(len(data)/2),data)
    data = np.array(data, dtype='h')
    # Apply FFT - real data so rfft used
    fourier=np.fft.rfft(data)
    fourier=np.abs(fourier)
    maxpos=fourier.argmax()
    return (maxpos,fourier[maxpos],np.mean(fourier[target-triggerdelta:target+triggerdelta]))
#
# commands specific to the apa102
#
class Pixels:
    PIXELS_N = 3
    def __init__(self):
        self.dev = apa102.APA102(num_led=self.PIXELS_N)
    def red(self):
        self.write([7,0,0,0,0,0,0,0,0])

    def green(self):
        self.write([0,0,0,0,7,0,0,0,0])

    def off(self):
        self.write([0] * 3 * self.PIXELS_N)

    def write(self, colors):
        for i in range(self.PIXELS_N):
            self.dev.set_pixel(i, int(colors[3*i]), int(colors[3*i + 1]), int(colors[3*i + 2]))

        self.dev.show()

pixels=Pixels()
def goodbye():
    pixels.off()

atexit.register(goodbye)


#
# Alarm on/off state changes
#
def alarmOn():
    #print("ON")
    pixels.red()
    pid=subprocess.Popen(['/usr/bin/python','./raiseAlarm.py']).pid
    #print("Pid = %d" % pid)
    
def alarmOff():
    pixels.green()
    
    #print("OFF")
    
class AlarmStatus():
    """Decide when to trigger alarm given inputs """
    
    def __init__(self,triggerpos,triggerthreshold):
        self.triggerpos=triggerpos
        self.triggerthreshold=triggerthreshold
        """
        Uses a state machine to determine if an alarm state has been reached. When we hear a beep we count up "onstep",
        if no beep we count down "offstep". Beeps do not correspond to sample intervals, and there may be false alarms, 
        so we need a number of beeps within an interval to trigger an alarm. 
        If the beeps stop before the alarm limit is reached we decay back to a rest state.
        """
        #
        # change these settings as required for your own setup
        #
        self.onstep=20
        self.offstep=1
        self.upperLimit=300
        self.lowerLimit=0
        self.triggerdelta=4

        self.count=0
        self.state=self.off

    def off(self,s):
        if s:
            self.count = self.onstep
            return self.countingup
        return self.off
    
    def countingup(self,s):
        if s:
            self.count += self.onstep
            if self.count >= self.upperLimit:
                alarmOn()
                return self.on
        else:
            self.count -= self.offstep
            if self.count <=0:
                return self.off
        return self.countingup
    
    def on(self,s):
        if not s:
            self.count= self.upperLimit - self.offstep
            return self.countingdown
        return self.on
    
    def countingdown(self,s):
        if s:
            self.count += self.onstep
            if self.count >= self.upperLimit:
                return self.on
        else:
            self.count -= self.offstep
            if self.count <=0:
                alarmOff()
                return self.off
        return self.countingdown
    
    def monitor(self,data):
        global timestart
        #
        # return loudest frequency, it's value and the value round the trigger frequency
        #
        maxpos,value,targetval=find_maximum(data, self.triggerpos,self.triggerdelta)
        #
        # trigger detected if trigger frequency over the threshold and it's the loudest.
        # Feel free to try other trigger algorithms
        #
        trigger=targetval > self.triggerthreshold and (maxpos > self.triggerpos - self.triggerdelta and maxpos < self.triggerpos + self.triggerdelta ) 
        if trigger:
            print("time %s maxpos %4d val %6.0f target %6.0f count %2d" % (time.strftime("%d %b %Y %H:%M:%S", time.gmtime()),maxpos,value, targetval,self.count))
        self.state=self.state(trigger)
            
                


#
# Set up audio
#
sample_rate = 16000
no_channels = 1
chunk = 2560 # Use a multiple of 8
data_in = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL,device='plughw:CARD=seeed2micvoicec,DEV=0')
data_in.setchannels(no_channels)
data_in.setrate(sample_rate)
data_in.setformat(aa.PCM_FORMAT_S16_LE)
data_in.setperiodsize(chunk)


alarm=AlarmStatus(646,80000.0) 
# trigger frequency of 646 and alarm threshold of 80000
# These figures determined by trial and error
#
pixels.green()
print("Ready")

timestart=time.time()
#
# repeat this loop until end of time
#
while True:
    #
    # Read data from device	
    #
    l,data = data_in.read()
    if l:
        try:
            if len(data) != (2 * no_channels * chunk):
                print("Frame Error")
            else:
                #
                # pass to monitor 
                #
                alarm.monitor(data)
                
        except Exception, e:
            print(e.message)
            raise e
    time.sleep(0.001)
