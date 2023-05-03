import machine
from machine import Pin, ADC 
import utime 

# Constants
OUTPUT_LEN = .1 #How long each bit will be outputted (held high or low) before next bit, in seconds
SENSOR_NUM = 0 #There are 3 vibration sensors, each with an individual number and key to identify it

#Initialize Prepherials
LED = Pin("LED",Pin.OUT)
out = Pin(2, Pin.OUT)
POT_Value = ADC(0) #Which ADC converter are we using for piezoelctric input
conversion_factor = 3.3/(65536) #Convert ADC output to voltage

#Which sensor number is this
if SENSOR_NUM == 0: 
    key = "1010"
if SENSOR_NUM == 1: 
    key = "10101010"
    
#Output 433 MHz RF to signal fall
def outputKey(num):
    print("printing ", num)
    for i in num:
        #print(i)
        out.value(int(i))
        utime.sleep(OUTPUT_LEN)

#-------------------Vibration section -----------------------------------------

#initialize last 1/10th of a second values
last20 = []
for i in range(20):
        last20.append(POT_Value.read_u16() * conversion_factor)
        utime.sleep(0.01)

#Main Application loop 
while True:
    curr = POT_Value.read_u16() * conversion_factor
    avg = sum(last20)/20
    if curr - .01 > avg: #threshold to detect vibration, subject to change
        LED.value(1)
        print("VOLTAGE SPIKE.  AVG:", avg, "CURR", curr)
        #Wait so not all 3 sensors send at once
        utime.sleep(OUTPUT_LEN*12*(SENSOR_NUM*2))
        #output key 3 times in a row because there is a samll chance it is not recieved
        outputKey(key)

    LED.value(0)
    last20.pop(0)
    last20.append(curr)
    utime.sleep(0.01)
