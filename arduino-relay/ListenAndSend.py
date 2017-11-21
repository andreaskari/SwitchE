import time
import serial 
import requests
import json
import sys
import datetime

BASE = 'http://52.15.86.194'
HEADER = {}

# Change the port name to match the port 
# to which your Arduino is connected. 
# serial_port_name = '/dev/tty.usbserial-A9007UX1' 
serial_port_name = '/dev/cu.usbmodem14231' 
ser = serial.Serial(serial_port_name, 9600, timeout=1)

delay = 1 # Delay in seconds

# Run once at the start
def setup():
    try:
        print 'Setup'
    except:
        print 'Setup Error'

# Run continuously forever
def loop(): 
    # Check if something is in serial buffer 
    if ser.inWaiting() > 0: 
        # Read green value form serial
        current = float(ser.readline())
        print 'Received from serial:', current 

        # Post current
        post_current(current)

        # Get IO
        value = get_IO()
        print 'Received from server:', value 

        # Write orange value to serial
        if value != None:
            ser.write(value) 

    # 5 second delay 
    time.sleep(5) 
    return

def get_IO():
    value = 0
    endpoint = '/getLastIO'
    query = {}
    response = requests.request('GET', BASE + endpoint, params=query, headers=HEADER, timeout=120)
    resp = json.loads(response.text)
    print(response.text)
    if resp['points-code'] == 200 and resp['value'] == 'true':
        value = 1
    return value

def post_current(value):
    endpoint = '/postCurrent/' + str(value)
    query = {}
    response = requests.request('POST', BASE + endpoint, params=query, headers=HEADER, timeout=120)
    resp = json.loads(response.text)
    print(response.text)

# Run continuously forever
# with a delay between calls
def delayed_loop():
    print 'Delayed Loop'

# Run once at the end
def close(): 
    try: 
        print 'Close Serial Port' 
        ser.close() 
    except: 
        print 'Close Error'
    
# Program Structure    
def main():
    setup()
    nextLoop = time.time()
    while(True):
        loop()
        if time.time() > nextLoop:
            nextLoop = time.time() + delay
            delayed_loop()
    close()

# Run the program
main()
