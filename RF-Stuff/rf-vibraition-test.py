import machine
from machine import Pin, ADC 
import utime 

 #-----------------rf portion------------------------------------------
#Initialize Prepherials
out = Pin(15, Pin.OUT)
#How long each bit will be outputted (held high or low) before next bit, in seconds
OUTPUT_LEN = .1
#There are 3 vibration sensors, each with an individual number and key to identify it
sensor_num = 0
key = "100" + "101" + "101" + "001"
#sensor_num = 1
#key = "110" + "010" + "101" + "001"
#sensor_num = 2
#key = "101" + "110" + "011" + "101"

utime.sleep(1*sensor_num)
def outputKey(num):
    for i in num:
        print(i)
        out.value(int(i))
        utime.sleep(OUTPUT_LEN)

#-------------------Vibration section -----------------------------------------
POT_Value = ADC(0) 
conversion_factor = 3.3/(65536)

#initialize last 1/10th of a second val

last20 = []
for i in range(20):
        last20.append(POT_Value.read_u16() * conversion_factor)
        utime.sleep(0.01)

#Main Application loop 
while True:
    curr = POT_Value.read_u16() * conversion_factor
    #print(curr)
    avg = sum(last20)/20
    if curr - .01 > avg:
        ##rf.value(1)
        print("VOLTAGE SPIKE.  AVG:", avg, "CURR", curr)
        #output key 3 times in a row because there is a samll chance it is not recieved
        outputKey(key)
        outputKey(key)
        outputKey(key)
    #else:
        #print(avg, curr)
    last20.pop(0)
    last20.append(curr)
    utime.sleep(0.01)
