"""
MIT License

Copyright (c) 2020 William A Pringle

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

import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile

samples=[
    ("mastrad2",6152,"Quiet Background"),
    ("noisymastrad2",6152,"Noisy Background"),
    ("vacuumfreezer",4130,"Vacuum Cleaner Background"),
]

for ss in samples:
    rate,data_in=scipy.io.wavfile.read("%s.wav" % ss[0])
    if len(np.shape(data_in))>1: data_in=np.sum(data_in,1)
    
    step=1024
    nrows=2
    ncols=1
    i=0
    
    while len(data_in)>1024*(i)*step : 
        x=data_in[1024*i*step:1024*(i+1)*step]
        print(x[0])
        i+=1
    
        nsamples = len(x)
        T = nsamples / rate
        t = np.linspace(0, T, nsamples, endpoint=False)
        
        plt.figure(i)
        plt.clf()
        plt.subplot(nrows,ncols,1)
        plt.suptitle(ss[2])
    
        plt.title('Raw signal')
        plt.plot(t, x)
    
        plt.xlabel('Time(sec)')
        
        fourier=np.fft.rfft(x)
        fourier = fourier / len(x)
        
        #calculate the frequency at each point in Hz
        freqArray = np.arange(0, (len(fourier)), 1.0) * (rate*1.0/len(x) )    
        plt.subplot(nrows,ncols,2)
        plt.title("Fourier Transform")
        plt.plot( freqArray/1000, np.abs(fourier))
        plt.xlabel('Frequency (kHz)')
        plt.ylabel('Power (dB)')
        
        plt.subplots_adjust(hspace=0.5)
    
        plt.show()
    
    
