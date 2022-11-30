# Sources: https://picockpit.com/raspberry-pi/everything-about-the-raspberry-pi-pico-w/#Connecting_to_WiFi 
# and https://core-electronics.com.au/guides/raspberry-pi-pico-w-create-a-simple-http-server/
# https://thepihut.com/blogs/raspberry-pi-tutorials/wireless-communication-between-two-raspberry-pi-pico-w-boards

##TODO: USE THIS ONE NEXT https://picockpit.com/raspberry-pi/stream-sensor-data-over-wifi-with-raspberry-pi-pico-w/

# Sources: https://picockpit.com/raspberry-pi/everything-about-the-raspberry-pi-pico-w/#Connecting_to_WiFi 
# and https://core-electronics.com.au/guides/raspberry-pi-pico-w-create-a-simple-http-server/
# https://thepihut.com/blogs/raspberry-pi-tutorials/wireless-communication-between-two-raspberry-pi-pico-w-boards

##TODO: USE THIS ONE NEXT https://picockpit.com/raspberry-pi/stream-sensor-data-over-wifi-with-raspberry-pi-pico-w/

import rp2
import network
import ubinascii
import machine
import urequests as requests
import time
import socket


page = open("index.html", "r")
html = page.read()
page.close()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# If you need to disable powersaving mode
# wlan.config(pm = 0xa11140)

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('mac = ' + mac)

# Other things to query
# print(wlan.config('channel'))
# print(wlan.config('essid'))
# print(wlan.config('txpower'))

# Load login data from different file for safety reasons
ssid = 'iPhone (44)'
pw = '6h0eupmr6hira'

wlan.connect(ssid, pw)

# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    timeout -= 1
    print('Waiting for connection...')
    time.sleep(1)

# Define blinking function for onboard LED to indicate error codes    
def blink_onboard_led(num_blinks):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)
    
# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth

wlan_status = wlan.status()
blink_onboard_led(wlan_status)

if wlan_status != 3:
    raise RuntimeError('Wi-Fi connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])
    
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
while True:
    cl, addr = s.accept()
    cl_file = cl.makefile('rwb', 0)
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break
    response = html
    
    response = response.replace('AccX', '0')
    response = response.replace('AccY', '1')
    response = response.replace('AccZ', '2')
    
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()

