# Program to read RGB values from a local Pico Web Server
# Connect to network
import network
import time
# secret import ssid, password
import socket
import random
from machine import Pin

button = Pin(0, Pin.IN, Pin.PULL_UP)
led = Pin('LED', Pin.OUT)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('PeaceisAwesome', '32439344')
while not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting to connect:")
    time.sleep(1)
 
# Should be connected and have an IP address
wlan.status() # 3 == success
wlan.ifconfig()
print(wlan.ifconfig())


while True:
    sensorData = 67
    if button.value() == 1:
        seq =1
    if seq == 1:
        ai = socket.getaddrinfo("192.168.137.41", 80) # Address of Web Server
        addr = ai[0][-1]

        # Create a socket and make a HTTP request
        s = socket.socket() # Open socket
        s.connect(addr)
        s.send(str(sensorData)) # Send request
        ss=str(s.recv(512)) # Store reply
        # Print what we received
        print(ss)
        # Set RGB LED here
        s.close()          # Close socket
    seq = 0


