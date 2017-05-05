#!/usr/bin/python

# ----------------------------------------------------------------------------
#  HW_Thread.py
#  Classes for communication with asynchronous hardware
#  written by Jonathan Foote jtf@rotormind.com 3/2013
#
#  Works with example Arduino code from 
#  https://github.com/headrotor/Python-Arduino-example
#  Share & enjoy!
#
# -----------------------------------------------------------------------------
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as  as published 
# by the Free Software Foundation http://www.gnu.org/licenses/gpl-2.0.html
# This program is distributed WITHOUT ANY WARRANTY use at your own risk blah blah


import requests
import serial #get from http://pyserial.sourceforge.net/
import sys
import time
import threading
import serial.tools.list_ports

currentSensor = ""


class GetHWPoller(threading.Thread):
  """ thread to repeatedly poll hardware
  sleeptime: time to sleep between pollfunc calls
  pollfunc: function to repeatedly call to poll hardware"""
  
  def __init__(self,sleeptime,pollfunc):

    self.sleeptime = sleeptime
    self.pollfunc = pollfunc  
    threading.Thread.__init__(self)
    self.runflag = threading.Event()  # clear this to pause thread
    self.runflag.clear()
      
  def run(self):
    self.runflag.set()
    self.worker()

  def worker(self):
    while(1):
      if self.runflag.is_set():
        self.pollfunc()
        time.sleep(self.sleeptime)
      else:
        time.sleep(1)

  def pause(self):
    self.runflag.clear()

  def resume(self):
    self.runflag.set()

  def running(self):
    return(self.runflag.is_set())

  def kill(self):
    print "WORKER END"
    sys.stdout.flush()
    self._Thread__stop()


class HW_Interface(object):
  """Class to interface with asynchrounous serial hardware.
  Repeatedly polls hardware, unless we are sending a command
  "ser" is a serial port class from the serial module """

  def __init__(self,ser,sleeptime):
    self.ser = ser
    self.sleeptime = float(sleeptime)
    self.worker = GetHWPoller(self.sleeptime,self.poll_HW)
    self.interlock = False  # set to prohibit thread from accessing serial port
    self.response = None # last response retrieved by polling
    self.sensorValue = ""
    self.counter = 0
    self.worker.start()
    self.callback = None
    self.verbose = True # for debugging

  def register_callback(self,proc):
    """Call this function when the hardware sends us serial data"""
    self.callback = proc
    #self.callback("test!")
	

    
  def kill(self):
    self.worker.kill()

  def reset(self):
    self.sensorValue = ""


  def sendToServer(self,name,rfid):
    uri = "http://asrama.esy.es/addrfid.php?rfid="+ rfid+ "&name="+name
    r = requests.get(uri)
    print(r)

  def getSensorValue(self):    
    if(1==2):
      print("x")

    
    

    #print(self.sensorValue)


  def write_HW(self,command):
    """ Send a command to the hardware"""
    while self.interlock: # busy, wait for free, should timout here 
      print "waiting for interlock"
      sys.stdout.flush()
    self.interlock = True
    self.ser.write(command + "\n")
    self.interlock = False

  def poll_HW(self):
    """Called repeatedly by thread. Check for interlock, if OK read HW
    Stores response in self.response, returns a status code, "OK" if so"""
    if self.interlock:
      if self.verbose: 
        print "poll locked out"
        self.response = None
        sys.stdout.flush()
      return "interlock" # someone else is using serial port, wait till done!
    self.interlock = True # set interlock so we won't be interrupted
    # read a byte from the hardware
    response = self.ser.read(1)
    self.interlock = False
    if response:
      if len(response) > 0: # did something write to us?
        response = response.strip() #get rid of newline, whitespace
        if len(response) > 0: # if an actual character
          if self.verbose:
            self.response = response
            self.sensorValue = self.sensorValue + response
            print(len(self.sensorValue))

            if (self.sensorValue == "OK"):
              print("Connected to Arduino")
              self.reset()
            elif (len(self.sensorValue) == 10):
              print("RFID Detected : " + self.sensorValue)
              name = raw_input("Nama : ")
              if (name == "x"):
                print("Abort...")
                self.reset()
              else:
                self.sendToServer(name,self.sensorValue)
                self.reset()



            currentSensor = self.sensorValue
            self.counter += 1
            sys.stdout.flush()
          if self.callback:
            #a valid response so send it
            self.callback(self.response)
        return "OK"
    return "null" # got no response


def my_callback(response):
  """example callback function to use with HW_interface class.
     Called when the target sends a byte, just print it out"""
  


"""Designed to talk to Arduino running very simple demo program. 
Sending a serial byte to the Arduino controls the pin13 LED: ascii '1'
turns it on and ascii '0' turns it off. 

When the pin2 button state changes on the Arduino, it sends a byte:
ascii '1' for pressed, ascii '0' for released. """

if __name__ == '__main__':
 
  
  print "Listing available port.."
  ports = list(serial.tools.list_ports.comports())
  for p in ports:
    print p

  portname = "COM11"
  portbaud = "115200"
  ser = serial.Serial(portname,portbaud,timeout=0)
  print "Opened port " + portname + " at " + str(portbaud) +  " baud"
  sys.stdout.flush()
  hw = HW_Interface(ser,0.1)
  hw.reset()
  print("Connecting to Arduino.. Please wait..")
  print("Connected... Getting sensor data..")

  while(1):
    hw.getSensorValue()
    
  #tidy up, or you can just Ctrl-C
  hw.kill()
  ser.close()
  sys.exit()
  

