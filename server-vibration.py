
import network
import socket
import time
from machine import Pin, ADC
import random
import gc
import urequests as requests
import json
a = Pin(0,Pin.IN,Pin.PULL_UP)
b = Pin(15,Pin.OUT)
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

# Listen for connections
def notification():
    seq = 0
    while True:
        endtime = time.time()
        interval = endtime - start
        print(interval)
        if a.value() ==0 and interval < 90:
            print("Button Pressed")
            seq = 1
            break
        if interval > 90:
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

def handleRequest():
    print("Entered if statement")
    seq = 1
    sensordata=float(request)
    if seq == 1:
        notification()
seq =0
while seq==0:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        print(request)
        if request:
            start = time.time()
            handleRequest()
        response = "Alerted Caregiver"
        cl.send(response)
        cl.close()
        time.sleep(0.1)
    except OSError as e:
        cl.close()
        print('connection closed')
        


