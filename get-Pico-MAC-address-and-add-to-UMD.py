from getmac import get_mac_address as gma
print(gma())

# Make sure that you are in the Python 3 interepreter by going into Preferences > Interpreter
# Make sure to switch back to RPI Pico after for your other code
# Go to add: https://www.umass.edu/it/news/20180119/connectgamingconsolesstreamingdeviceswirelessnetworkresidentialareas
# Add UMass device as other and give the Mac address


##The Above only works for the local computer
## The below will give your pico mac

import rp2
import network
import ubinascii
import machine
import urequests as requests
import time
import socket


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
ssid = 'UMASS-DEVICES'
pw = 'GoUMass!'

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



#https://picockpit.com/raspberry-pi/everything-about-the-raspberry-pi-pico-w/#Connecting_to_WiFi
    
