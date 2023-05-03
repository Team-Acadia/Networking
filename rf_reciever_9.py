import machine
from machine import Pin
import time
import utime

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

for i in range(10000000000):
        #vibration listening
        reading1 = analog_value1.read_u16()
        if reading1 > 58000:
            prev1 = 1
            print("ADC: ", reading1)
        elif reading1 < 25000:
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
                #allow time for other vibration sensors to also send thier data
                vibrationKey = []
                vibrations_sensed[0] = 1
            elif vibrationKey == vibrationKey1:
                print("Found vibrationKey1: ", vibrationKey)
                #2nd sensor to send data
                vibrationKey = []
                vibrations_sensed[1] = 1
            else:
                print("UNRECOGNIZED VIBRATION KEY: ", vibrationKey)
                vibrationKey = []
        
        #mmwave listening
        reading2 = analog_value2.read_u16()
        if reading2 > 60000:
            prev2 = 1
            print("ADC: ", reading2)
        elif reading2 < 15000:
            if prev2 == 1:
                bitsQueue2.append(1)
                bitsQueue2.append(0)
                cyclesToWait2 = 20
            prev2 = 0
            print("ADC: ", reading2)
        #Wait for next potential bit
        if cyclesToWait2 != -1:
            cyclesToWait2 = cyclesToWait - 1
            if cyclesToWait2 == 0:
                print("FOUND: ", bitsQueue2)
                mmwaveKey = bitsQueue2
                
        #mmwave key matching
        if mmwaveKey != []:
            if mmwaveKey == mmwaveKey0:
                print("Found mmwaveKey0: ", bitsQueue2)
                mmWave_status = 1
                mmwaveKey = []
            elif mmwaveKey == mmwaveKey1:
                print("Found mmwaveKey1: ", bitsQueue2)
                mmWave_status = 2
                mmwaveKey = []
            else:
                print("UNRECOGNIZED MMWAVE KEY: ", mmwaveKey)
                mmwaveKey = []
        
        #print("Vibration: ", vibrations_sensed, "mmWave: ", mmWave_status)
        time.sleep(POLLING_FREQUENCY)
