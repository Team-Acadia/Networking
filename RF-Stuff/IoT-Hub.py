import machine
from machine import Pin
import time
import utime
import network
import urequests

#------------Buzzer to check if running ---------------

b = Pin(16,Pin.OUT)

# Generate a 2 kHz square wave for 1 second
for i in range(1000):
    b.on()
    time.sleep_us(250)  # 50% duty cycle
    b.off()
    time.sleep_us(250)

b.off()

print("searching for wifi connection")
SSID = "PeaceisAwesome"
PASSWORD = "32439344"
#connect to Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    pass
print("wifi connected")
URL = "https://server-domum.herokuapp.com/"
def SendToAppOne():
    DATA = {"data": "Fall detected by vibration 1"}
    response = urequests.post(URL, json=DATA)
def SendToAppTwo():
    DATA = {"data": "Fall detected by vibration 2"}
    response = urequests.post(URL, json=DATA)
def SendToAppThree():
    DATA = {"data": "Fall detected by vibration 3"}
    response = urequests.post(URL, json=DATA)
#This code listens for an RF signal from 3 different vibration sensors reporting a fall. At rest, the RF reciever reads noise, random 0s and 1s.
#Therefore, a fall cannot just be signalled by a high pulse from a sensor, so each has an ID it sends in binary
#Also, each vibration sensor's output signal is varried in time so their signals don't collide.

#Constants
POLLING_FREQUENCY = .02 #how often the input is checked
WAIT_AFTER_RCV = 4/POLLING_FREQUENCY #how many seconds to wait and listen for more data after first message

# Set up the input pin for IR sensor
rf = Pin(2, Pin.IN, Pin.PULL_DOWN)

#Vibration sensors IDs marking a fall
key_0 = "1010" #sensor num: 0
key_1 = "10101010" #sensor num: 1

#Initailize variables
vibrations_sensed = [0,0] #List of which sensors have detected a fall
mmWave_status = 0
cycles_to_wait = -1 #How long to wait for other sensors to report a fall

#Keys must be int arrays. Listed as strings above for readability 
vibrationKey0 = [0]*len(key_0)
vibrationKey1 = [0]*len(key_1)
mmWaveKey0 = [0]*len(key_0)
mmWaveKey1 = [0]*len(key_1)
for i in range(0,len(key_0)): 
  vibrationKey0[i]= int(key_0[i])
  mmWaveKey0[i] = int(key_0[i])

for i in range(0,len(key_1)): 
  mmWaveKey1[i] = int(key_1[i])
  vibrationKey1[i]= int(key_1[i])


# Listen for connections
def button():
    for i in range(100000):
        b.on()
        time.sleep_us(250)  # 50% duty cycle
        b.off()
        time.sleep_us(250)
        if a.value() == 1:
            print("Button Pressed")
            return
    print("Button not pressed in time")
    return

def notification(start):
    seq = 0
    while True:
        endtime = time.time()
        interval = endtime - start
        #print(interval)
        if a.value() ==1 and interval < 90:
            print("Button Pressed")
            seq = 1
            return
        if interval > 10:
            print("Not pressed in time")
            break
        if seq == 0:
            b.value(1)
            time.sleep(.001)
            b.value(0)
            time.sleep(.001)
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
        response = requests.post('https://api.pushbullet.com/v2/pushes', headers=headers, data=json.dumps(data))
        # Print the status code of the HTTP response
        return

#vibration
analog_value1 = machine.ADC(28)
bitsQueue1 = []
cyclesToWait1 = -1
prev1 = 0
vibrationKey = []
#mmwave detection
analog_value2 = machine.ADC(27)
bitsQueue2 = []
cyclesToWait2 = -1
prev2 = 0
mmwaveKey = []
#button pin
a = Pin(26,Pin.IN,Pin.PULL_DOWN)

#time.gmtime()[4:6] get minute and second
sensorTimes = [[-1,-1], [-1,-1], [-1,-1]]
while(True):
        #vibration listening
        reading1 = analog_value1.read_u16()
        if reading1 > 58000:
            prev1 = 1
            print("ADC: ", reading1)
        elif reading1 < 32000:
            if prev1 == 1:
                bitsQueue1.append(1)
                bitsQueue1.append(0)
                cyclesToWait1 = 40
            prev1 = 0
            print("ADC: ", reading1)
        #Wait for next potential bit
        if cyclesToWait1 != -1:
            cyclesToWait1 = cyclesToWait1 - 1
            if cyclesToWait1 == 0:
                print("FOUND: ", bitsQueue1)
                vibrationKey = bitsQueue1
                
        #Vibraion key matching
        if vibrationKey != []:
            bitsQueue1 = []
            if vibrationKey == vibrationKey0:
                print("Found vibrationKey0: ", vibrationKey)
                SendToAppOne()
                #allow time for other vibration sensors to also send thier data
                vibrationKey = []
                vibrations_sensed[0] = 1
                sensorTimes[0] = time.gmtime()[4:6]
            elif vibrationKey == vibrationKey1:
                print("Found vibrationKey1: ", vibrationKey)
                SendToAppTwo()
                #2nd sensor to send data
                vibrationKey = []
                vibrations_sensed[1] = 1
                sensorTimes[1] = time.gmtime()[4:6]
            else:
                print("UNRECOGNIZED VIBRATION KEY: ", vibrationKey)
                vibrationKey = []
        
        #mmwave listening
        reading2 = analog_value2.read_u16()
        #print(reading2)
        if reading2 > 60000:
            prev2 = 1
            print("ADC2: ", reading2)
        elif reading2 < 30000:
            if prev2 == 1:
                bitsQueue2.append(1)
                bitsQueue2.append(0)
                cyclesToWait2 = 20
            prev2 = 0
            print("ADC2: ", reading2)
        #Wait for next potential bit
        if cyclesToWait2 != -1:
            cyclesToWait2 = cyclesToWait2 - 1
            if cyclesToWait2 == 0:
                print("FOUND: ", bitsQueue2)
                mmwaveKey = bitsQueue2
                
        #mmwave key matching
        if mmwaveKey != []:
            bitsQueue2 = []
            if mmwaveKey == mmWaveKey0:
                print("Found mmWaveKey0: ", mmwaveKey)
                SendToAppThree()
                mmWave_status = 1
                mmwaveKey = []
                sensorTimes[2] = time.gmtime()[4:6]
            elif mmwaveKey == mmWaveKey1:
                print("Found mmWaveKey1: ", mmwaveKey)
                SendToAppThree()
                mmWave_status = 1
                mmwaveKey = []
                sensorTimes[2] = time.gmtime()[4:6]
            else:
                print("UNRECOGNIZED MMWAVE KEY: ", mmwaveKey)
                mmwaveKey = []
            
        
        
        if (mmWave_status + vibrations_sensed[0] + vibrations_sensed[1]) >= 2:
            button()
            if a.value() == 1:
                vibrations_sensed = [0,0]
                mmWave_status = 0
            else:
                vibrations_sensed = [0,0]
                mmWave_status = 0
                start = time.time()
                notification(start)
                
        #delete sensor data if older than 20 seconds
        currentTime = time.gmtime()[4:6]
        for i in range(3):
            if (sensorTimes[i][0] == -1):
                continue
            sensorSeconds = sensorTimes[i][0]*60 + sensorTimes[1][1] + 20
            curSeconds = currentTime[0]*60 + currentTime[1]
            if sensorSeconds < curSeconds or (currentTime[0] == 59 and sensorTimes[1][0] == 0):
                sensorTimes[i] = [-1, -1]
                if i == 0:
                    vibrations_sensed[0] = 0
                elif i == 1:
                    vibrations_sensed[1] = 0
                elif i == 2:
                    mmWave_status = 0
                print("removing sensor:",i," because of timeout")
        
        #print("Vibration: ", vibrations_sensed, "mmWave: ", mmWave_status)
        time.sleep(POLLING_FREQUENCY)
        
