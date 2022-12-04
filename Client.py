# Program to read RGB values from a local Pico Web Server
# Tony Goodhew 5th July 2022
# Connect to network
import network
import time
# secret import ssid, password
import socket

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
    ai = socket.getaddrinfo("192.168.137.67", 80) # Address of Web Server
    addr = ai[0][-1]

    # Create a socket and make a HTTP request
    s = socket.socket() # Open socket
    s.connect(addr)
    s.send(b"SEND Data") # Send request
    ss=str(s.recv(512)) # Store reply
    # Print what we received
    print(ss)
    # Set RGB LED here
    s.close()          # Close socket
    time.sleep(0.2)    # wait

