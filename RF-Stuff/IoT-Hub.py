import machine
from machine import Pin
import time
import utime
import network
import urequests
import json
#------------------Defining Pins--------------------------------------------------------------------------------------
# Define the pins used for various components
a = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_DOWN)  # Input pin for button
b = machine.Pin(16, machine.Pin.OUT)  # Output pin for buzzer
rf = Pin(2, Pin.IN, Pin.PULL_DOWN)  # Input pin for RF sensor
analog_value1 = machine.ADC(28)  # Vibration detection sensor
analog_value2 = machine.ADC(27)  # mmWave detection sensor

#-------------------------Function Definitions---------------------------------------------------------------------------
# Function to generate a square wave for the buzzer
def buzzer():
    for i in range(1000):  # Generate a 2 kHz square wave for 1 second
        b.value(1)
        time.sleep_us(250)  # 50% duty cycle
        b.value(0)
        time.sleep_us(250)

# Function to send a fall notification to the web server for vibration sensor 1
def SendToAppOne():
    DATA = {"data": "Fall detected by vibration 1"}
    response = urequests.post(URL, json=DATA)

# Function to send a fall notification to the web server for vibration sensor 2
def SendToAppTwo():
    DATA = {"data": "Fall detected by vibration 2"}
    response = urequests.post(URL, json=DATA)

# Function to send a fall notification to the web server for vibration sensor 3
def SendToAppThree():
    DATA = {"data": "Fall detected by vibration 3"}
    response = urequests.post(URL, json=DATA)

# Function to convert the RF reading to 0 or 1
def adcToDi1(reading1, cyclesToWait1, prev1):
    if reading1 > 58000:
        prev1 = 1
       # print("ADC: ", reading1)
    elif reading1 < 32000:
        if prev1 == 1:
            bitsQueue1.append(1)
            bitsQueue1.append(0)
            cyclesToWait1 = 40
        prev1 = 0
        #print("ADC: ", reading1)
    return cyclesToWait1, prev1
def adcToDi2(reading2, cyclesToWait2, prev2):
    if reading2 > 60000:
        prev2 = 1
        #print("ADC2: ", reading2)
    elif reading2 < 30000:
        if prev2 == 1:
            bitsQueue2.append(1)
            bitsQueue2.append(0)
            cyclesToWait2 = 20
        prev2 = 0
        #print("ADC2: ", reading2)
    return cyclesToWait2, prev2
# Function to send a fall notification using Pushbullet API
def notification(start):
    vibrations_sensed = [0,0]
    mmWave_status = 0
    seq = 0
    while True:
        endtime = time.time()
        print(start)
        print(endtime)
        print("interval: ",endtime-start)
        interval = endtime - start
        if a.value() == 1 and interval < 10:
            print("Button Pressed")
            seq = 1
            return
        if interval > 10:
            print("Not pressed in time")
            break
        if seq == 0:
            buzzer()
        time.sleep(0.001)
    if seq == 0:
        # Define the Pushbullet API key
        API_KEY = 'o.lZZCj1hPZjpBhZ6y9bMA7bqAsaoQN81Z'
        # Define the notification title and body
        title = "Fall Detected!"
        body = "Vibration Sensor detected a fall, please login to view more"
        # Define the headers for the HTTP POST request
        headers = {
                       'Authorization': 'Bearer ' + API_KEY,
            'Content-Type': 'application/json'
        }
        # Define the data for the HTTP POST request
        data = {
            'type': 'note',
            'title': title,
            'body': body
        }
        # Send the HTTP POST request to the Pushbullet API
        response = urequests.post('https://api.pushbullet.com/v2/pushes', headers=headers, data=json.dumps(data))
        # Print the status code of the HTTP response
        return

#-----------------------------Connecting to Wifi------------------------------------------------------------------------
print("Wifi connecting")
SSID = "PeaceisAwesome"
PASSWORD = "32439344"
# Connect to Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    pass
print("wifi connected")

buzzer()


#--------------------------------------Set up post request to web servers-------------------------------------------------
URL = "https://server-domum.herokuapp.com/"

#----------------------------------------RF Section----------------------------------------------------------------------------
"""
This code listens for an RF signal from 3 different vibration sensors reporting a fall. 
At rest, the RF receiver reads noise, random 0s and 1s.
Therefore, a fall cannot just be signaled by a high pulse from a sensor, so each has an ID it sends in binary.
Also, each vibration sensor's output signal is varied in time so their signals don't collide.
"""
#-----------------Defining Constants-----------------------------
POLLING_FREQUENCY = .02  # How often the input is checked
WAIT_AFTER_RCV = 4 / POLLING_FREQUENCY  # How many seconds to wait and listen for more data after the first message

# Keys for vibration sensors
key_0 = "1010"  # Sensor number 1
key_1 = "10101010"  # Sensor number 2
Key_2 = "110001110001"

#--------------Defining Variables---------------------------------
vibrations_sensed = [0,0]  # List of which sensors have detected a fall
mmWave_status = 0
cycles_to_wait = -1  # How long to wait for other sensors to report a fall
POLLING_FREQUENCY = .02  # How often the input is checked
WAIT_AFTER_RCV = 4 / POLLING_FREQUENCY  # How many seconds to wait and listen for more data after the first message
vibrationKey0 = [0]*len(key_0)
vibrationKey1 = [0]*len(key_1)
mmWaveKey0 = [0]*len(key_0)
mmWaveKey1 = [0]*len(key_1)
vibrationKey0 = [int(bit) for bit in key_0.split()]
vibrationKey1 = [int(bit) for bit in key_1.split()]
bitsQueue1 = []  # Queue for storing bits from vibration sensor 1
cyclesToWait1 = -1  # How long to wait for the next bit from vibration sensor 1
prev1 = 0  # Previous state of the vibration sensor 1
vibrationKey = []  # Stores the received key from vibration sensors
bitsQueue2 = []  # Queue for storing bits from mmWave sensor
cyclesToWait2 = -1  # How long to wait for the next bit from mmWave sensor
prev2 = 0  # Previous state of the mmWave sensor
mmwaveKey = []  # Stores the received key from mmWave sensor
sensorTimes = [[-1,-1], [-1,-1], [-1,-1]]  # Keeps track of the timestamp of fall detection for each sensor

#--------------------------------------------------------Main While Loop---------------------------------------------------------

while True:
    # Vibration listening
    reading1 = analog_value1.read_u16()
    cyclesToWait1, prev1 = adcToDi1(reading1, cyclesToWait1, prev1)

#-------------------------------------------------------Wait for next potential bit-------------------------------------
    if cyclesToWait1 != -1:
        cyclesToWait1 = cyclesToWait1 - 1
        if cyclesToWait1 == 0:
            vibrationKey = bitsQueue1

#------------------------------------------------------Vibration key matching-----------------------------------------------
    if vibrationKey != [] :
        bitsQueue1 = []
        vibrationKey =  [int("".join(str(bit) for bit in vibrationKey))]
        if vibrationKey == vibrationKey0:
            print("Found vibrationKey0: ", vibrationKey)
            SendToAppOne()
            # Allow time for other vibration sensors to also send their data
            vibrationKey = []
            vibrations_sensed[0] = 1
            sensorTimes[0] = time.gmtime()[4:6]
        elif vibrationKey == vibrationKey1:
            print("Found vibrationKey1: ", vibrationKey)
            SendToAppTwo()
            # 2nd sensor to send data
            vibrationKey = []
            vibrations_sensed[1] = 1
            sensorTimes[1] = time.gmtime()[4:6]
        else:
            print("Actual Vibration Key1: ", vibrationKey1)
            print("UNRECOGNIZED VIBRATION KEY: ", vibrationKey)
            vibrationKey = []

#-----------------------------------------------------------mmWave listening-------------------------------------------------------
    reading2 = analog_value2.read_u16()
    cyclesToWait2, prev2 = adcToDi2(reading2, cyclesToWait2, prev2)
    #-------------------------------------------------------Wait for next potential bit--------------------------------------------
    if cyclesToWait2 != -1:
        cyclesToWait2 = cyclesToWait2 - 1
        if cyclesToWait2 == 0:
            mmwaveKey = bitsQueue2
    #------------------------------------------------------------mmWave key matching-------------------------------------------------
    if mmwaveKey != []:
        bitsQueue2 = []
        if mmwaveKey == mmWaveKey0:
            print("Found mmWaveKey0: ", mmwaveKey)
            SendToAppThree()
            mmWave_status = 1
            mmwaveKey = []
            sensorTimes[2] = time.gmtime()[4:6]
        else:
            print("UNRECOGNIZED MMWAVE KEY: ", mmwaveKey)
            mmwaveKey = []
    if (mmWave_status + vibrations_sensed[0] + vibrations_sensed[1]) >= 2:
        notification(time.time())
        vibrations_sensed[0] = 0
        vibrations_sensed[1] = 0
        print("Out of notification")
#------------------------------------------------------------delete sensor data if older than 20 seconds--------------------------
    currentTime = time.gmtime()[4:6]
    for i in range(3):
        if sensorTimes[i][0] == -1:
            continue
        sensorSeconds = sensorTimes[i][0] * 60 + sensorTimes[1][1] + 20
        curSeconds = currentTime[0] * 60 + currentTime[1]
        if sensorSeconds < curSeconds or (currentTime[0] == 59 and sensorTimes[1][0] == 0):
            sensorTimes[i] = [-1, -1]
            if i == 0:
                vibrations_sensed[0] = 0
            elif i == 1:
                vibrations_sensed[1] = 0
            elif i == 2:
                mmWave_status = 0
            print("Removing sensor:", i, " because of timeout")
    time.sleep(POLLING_FREQUENCY)




