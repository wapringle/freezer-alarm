#!/usr/bin/env python
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

import sys,os
import urllib2
import re,time
import subprocess


#
# Change these for your own setup
#
host="192.168.1.6:8080" # domestic radio
warningURI="http://192.168.1.9:8000/freezer.mp3" # freezer PI

#
# This is the framework of the message sent to the radio
#
def soapcall(action,extras="",service="AVTransport"):
    soap_body = """
    <?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
       <s:Body>
          <u:%(action)s xmlns:u="urn:schemas-upnp-org:service:%(service)s:1">
             <InstanceID>0</InstanceID>
             %(extras)s
          </u:%(action)s>
       </s:Body>
    </s:Envelope>
    """ % locals()

    localHost=host
    request= urllib2.Request(url="http://%(localHost)s/%(service)s/control" % locals(), data=soap_body)
    request.add_header('Content-Type', 'text/xml; charset=utf-8')
    request.add_header('SOAPAction', "\"urn:schemas-upnp-org:service:$(service)s:1#%(action)s\"" % locals())

    try:
        response=urllib2.urlopen(request)
        return response.read()
    except urllib2.HTTPError,e:
        print action,e.message 
        sys.exit(1)

#
# as implemented by specific messages
#
def GetPositionInfo():
    return soapcall("GetPositionInfo")

def GetTransportInfo():
    return soapcall("GetTransportInfo")

def Play():
    return soapcall("Play","<Speed>1</Speed>",)

def SetAVTransportURI(warningURI):
    return soapcall("SetAVTransportURI",extras="<CurrentURI>%s</CurrentURI><CurrentURIMetaData></CurrentURIMetaData>" % warningURI) 

def SetVolume(volume):
    return soapcall("SetVolume",extras="<Channel>Master</Channel><DesiredVolume>%(volume)s</DesiredVolume>" % locals(),service="RenderingControl")


def main():
    #
    # Start a webserver to serve the warning mp3 file
    #
    popen = subprocess.Popen(["/usr/bin/python2.7", "-mSimpleHTTPServer","8000"])
    time.sleep(2)
    #
    # Make it LOUD
    #
    SetVolume(70)
    SetAVTransportURI(warningURI)
    
    #
    # Try repeating the warning message until the radio has been turned off.
    # This is given by the transport state NO_MEDIA_PRESENT (didn't make sense to me either)
    #
    CurrentTransportState="STOPPED"
    while CurrentTransportState != "NO_MEDIA_PRESENT":
        if CurrentTransportState == "STOPPED":
            Play()
        time.sleep(1)
        try:
            CurrentTransportState=re.findall("<CurrentTransportState>(.*)</CurrentTransportState>", GetTransportInfo())[0]
        except:
            CurrentTransportState=None
                
    #
    # Close down server
    #
    popen.kill()  

main()    

