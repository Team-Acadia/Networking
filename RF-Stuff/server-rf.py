
import network
import socket
import time
from machine import Pin, ADC
import gc
import urequests as requests
import json
import _thread


#------------Buzzer to check if running ---------------

b = Pin(16,Pin.OUT)
# Generate a 2 kHz square wave for 1 second
for i in range(1000):
    b.on()
    time.sleep_us(250)  # 50% duty cycle
    b.off()
    time.sleep_us(250)

b.off()

#--------------Defining the wifi components ----------------------------------------------
#rf_pin = Pin(26,Pin.IN)
a = Pin(26,Pin.IN,Pin.PULL_DOWN)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("PeaceisAwesome", "32439344")
# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)
#----------------------- Rf section -----------------------------------------------
#This code listens for an RF signal from 3 different vibration sensors reporting a fall. At rest, the RF reciever reads noise, random 0s and 1s.
#Therefore, a fall cannot just be signalled by a high pulse from a sensor, so each has an ID it sends in binary
#Also, each vibration sensor's output signal is varried in time so their signals don't collide.

#Constants
POLLING_FREQUENCY = .02 #how often the input is checked
WAIT_AFTER_RCV = 2 #how many seconds to wait and listen for more data after first message

# Set up the input pin for IR sensor
rf = Pin(28, Pin.IN, Pin.PULL_DOWN)
#Vibration sensors IDs marking a fall
key_0 = "100" + "101" + "101" + "001" #sensor num: 0
key_1 = "110" + "010" + "101" + "001" #sensor num: 1
key_2 = "101" + "110" + "011" + "101" #sensor num: 2
#Initailize variables
bitsQueue = [0]*(12*5) #Running Queue of last 12 bits to search for IDs
vibrations_sensed = [0,0,0] #List of which sensors have detected a fall
cycles_to_wait = -1 #How long to wait for other sensors to report a fall
#Keys must be int arrays. Listed as strings above for readability 
keyLength = len(key_0)
key0 = [0]*12
key1 = [0]*12
key2 = [0]*12
for i in range(0,keyLength): 
  key0[i]= int(key_0[i])
  key1[i]= int(key_1[i])
  key2[i]= int(key_2[i])
keys = [key0, key1, key2]
#--------------------------Main code ---------------------------------------
# Listen for connections
def notification(start):
    seq = 0
    while True:
        endtime = time.time()
        interval = endtime - start
        print(interval)
        if a.value() ==1 and interval < 90:
            print("Button Pressed")
            seq = 1
            break
        if interval > 10:
            print("Not pressed in time")
            break
        if seq == 0:
            b.value(1)
            time.sleep(.001)
            b.value(0)
            time.sleep(.001)
    if seq == 0:
        gc.collect()
        resp = None
        try:
            body = "Sensor Data"
            title = "Fall Detected"
            data_sent = {"type":"note","title":title,"body":body}
            API_KEY = 'o.Ywi05DOBMqM3jdGJ5FdGEwd6STLclHuj'
            pb_headers = {
            'Authorization': 'Bearer ' + API_KEY,
            'Content-Type': 'application/json',
            'Host': 'api.pushbullet.com'
            }
            resp = requests.post('https://api.pushbullet.com/v2/pushes',data=json.dumps(data_sent),headers=pb_headers)
        except Exception as e:
            if isinstance(e, OSError) and resp:
                resp.close()
            value = {"error":e}
        gc.collect()
    return
def checkMatch(bitsQueue):
    avgBits = []
    prev = 2
    consecutive = 1
    for i in bitsQueue:
        if prev == 2:
            prev = i
            continue
        
        #print(avgBits, i, consecutive, prev)
        if i == 1:
            if prev == 1:
                consecutive = consecutive + 1
            else:
                if consecutive > 3:
                    for i in range(consecutive//4):
                        avgBits.append(0)
                    consecutive = 1
                    prev = 1
                    #print("prev", prev)
                else:
                    return -1
                
        elif i == 0:
            if prev == 0:
                consecutive = consecutive + 1
            else:
                if consecutive > 3:
                    for i in range(consecutive//4):
                        avgBits.append(1)
                    consecutive = 1
                    prev = 0
                    #print("prev", prev)
                else:
                    return -1
    if bitsQueue[-1] == 0:
        for i in range(consecutive//4):
            avgBits.append(0)
    if bitsQueue[-1]:
        for i in range(consecutive//4):
            avgBits.append(1)
    if avgBits in keys:
        print("FOUND KEY MATCH")
        handleRequest(time.time())
    print("avgBits: ", avgBits)
    return avgBits
def handleRequest(start):
    print("Entered if statement")
    seq = 1
    if seq == 1:
        notification(start)
def handleRf():
    cycles_to_wait = -1 #How long to wait for other sensors to report a fall
    while True:
        rf_value = rf.value()
        bitsQueue.append(rf_value)
        bitsQueue.pop(0)
        #check if current bit string matches a key
        avgBits = checkMatch(bitsQueue)
        if avgBits == key0:
                print("Found key0: ", bitsQueue)
                #allow time for other vibration sensors to also send thier data
                vibrations_sensed[0] = 1
        if avgBits == key1:
                print("Found key1: ", bitsQueue)
                #2nd sensor to send data
                vibrations_sensed[1] = 1
        if avgBits == key2:
                print("Found key2: ", bitsQueue)
                #Final sensor to send data
                vibrations_sensed[2] = 1
                #break
        time.sleep(POLLING_FREQUENCY)
def handleWifi():
    #-----------Checking to see If I get a wifi connection from a client------------
    while seq==0:
        try:
            print("test2")
            cl, addr = s.accept()
            print('client connected from', addr)
            request = cl.recv(1024)
            print(request)
            if request:
                start = time.time()
                handleRequest(start)
            response = "Alerted Caregiver"
            cl.send(response)
            cl.close()
            time.sleep(0.1)
        except OSError as e:
            cl.close()
            print('connection closed')
            
seq =0

_thread.start_new_thread(handleWifi,())
handleRf()




